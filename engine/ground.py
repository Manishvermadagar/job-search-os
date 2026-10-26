#!/usr/bin/env python3
"""ground.py - claim grounding for application answers.

The most common defect in application writing is a sentence that asserts
something with nothing behind it: a generalisation dressed as experience, an
absence claim ("a company that had no process"), a figure that appears in no
source, or a true fact about one team restated about the whole company.

For every sentence this fetches the best supporting lines from the career bank,
the posting and company-research.md, and marks it SUPPORTED, REVIEW or
UNSUPPORTED. Every UNSUPPORTED sentence then needs a recorded disposition.

What this is NOT: a truth oracle. It cannot tell a factual claim from rhetoric.
It makes every unsupported sentence VISIBLE and INDIVIDUALLY ANSWERED, turning a
silent omission into a recorded decision.

Deliberately lexical (BM25-style IDF overlap), not embeddings: deterministic,
auditable, no network, no dependencies, and it cannot return a plausible wrong
chunk.

    python engine/ground.py check <folder> --draft <answer.md> [--out grounding.json]
"""
import argparse, json, math, os, re, sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "checks"))
from common import career_bank, read  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

STOP = set("""a an the and or but if then than that this these those of in on at to for with by from as is are was
were be been being it its it's he she they them their there here we you your i my me our us do does did not no so
such can could would should may might will shall have has had which who whom whose what when where why how all any
both each few more most other some only own same very just also into over under about after before during while
because although though however therefore thus one two three get got make made take taken""".split())

# Sentences carrying these signals assert something beyond a plain statement of
# fact. They are where unsupported claims hide.
RISK = [
    (r"\b(in my experience|what i(?:'ve| have) found|in my case|i(?:'ve| have) found that)\b",
     "LAUNDERING", "puts an experiential frame in front of a generalisation, which makes it sound sourced without sourcing it"),
    (r"\b(only ever|nobody|no one|everybody|everyone|always|never|invariably|in every case|all of them|none of them)\b",
     "ABSOLUTE", "unhedged universal"),
    (r"\b(most|plenty|many|few|majority) of (them|those|these|your|their|the)\b",
     "QUANTIFIER-3P", "quantified claim about a third party's population"),
    (r"\b(had no|have no|has no|with no|there (?:was|is|were) no|none existed|no prior|"
     r"first[- ]ever|the first \w+ (?:to|in|at|who)\b|from scratch|the only)\b",
     "ABSENCE-OR-FIRST", "absence or precedence claim - check WHICH NOUN the qualifier governs in the source"),
    (r"\byour (customers|sellers|users|clients|borrowers|members|queue|team|partners)\b",
     "EMPLOYER-OPERATION", "asserts something about the employer's own operation or customers"),
    (r"\b(19|20)\d\d\b", "YEAR", "a year must match the source that owns it - a founding year is not a product launch"),
    (r"\b\d[\d,]*(\.\d+)?%?\b", "NUMBER", "a figure must trace to a source"),
]

# Collective scopes a narrow fact tends to migrate onto.
SCOPE_BREADTH = (r"\b(?:those|these|the|all|every|each|both|five|four|our)\s+"
                 r"(?:\w+\s+){0,2}?"
                 r"(?:teams|functions|departments|operation|operations|company|"
                 r"business|org|organisation|organization|firm)\b"
                 r"|\b(?:company[- ]wide|across the (?:company|business|org\w*)|"
                 r"the whole (?:company|business|operation|team))\b")

# High topical overlap MASKS a wrong qualifier ("at a company that had no
# escalation process" overlaps heavily with real escalation lines), so these
# flags are never cleared by similarity.
BLOCKING = {"LAUNDERING", "ABSOLUTE", "ABSENCE-OR-FIRST", "QUANTIFIER-3P",
            "EMPLOYER-OPERATION", "SCOPE-BREADTH"}

SKIP_LINE = re.compile(r"@|\+\d{1,3}[-\s]?\d{6,}|github\.com|linkedin\.com|^\s*DEMO\b", re.I)


def sentences(text):
    # Headings, contact lines and the demo label are not claims. Drop them before
    # splitting, or a heading merges into the first sentence.
    keep = [ln for ln in text.splitlines()
            if not ln.strip().startswith("#") and not SKIP_LINE.search(ln)]
    text = re.sub(r"\s+", " ", "\n".join(keep).strip())
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"'“])", text)
    return [p.strip() for p in parts if p.strip()]


def norm(w):
    return w.strip(".,'-")


def toks(s):
    return [w for w in re.findall(r"[a-z0-9$%.,'-]+", s.lower())
            if norm(w) and norm(w) not in STOP and len(norm(w)) > 2]


class Index:
    def __init__(self):
        self.units = []   # (label, lineno, text, Counter)
        self.df = Counter()

    def add_file(self, path, label, verbatim_only=False):
        """verbatim_only: if the posting file marks a '## ... VERBATIM' section,
        index only that section. Notes written above the posting by whoever saved
        it must not be able to 'support' a claim about the employer. Line numbers
        are preserved so a SOURCE:file:line disposition still points at the real line."""
        if not os.path.exists(path):
            return 0
        raw = read(path).splitlines()
        start = 0
        if verbatim_only:
            for i, line in enumerate(raw):
                if re.search(r"^##+\s*.*VERBATIM", line, re.I):
                    start = i + 1
                    break
        n = 0
        for i, line in enumerate(raw, 1):
            line = line.strip()
            if i <= start or len(line) < 25:
                continue
            c = Counter(norm(t) for t in toks(line))
            if not c:
                continue
            self.units.append((label, i, line, c))
            for t in set(c):
                self.df[t] += 1
            n += 1
        return n

    def all_text(self):
        if not hasattr(self, "_all"):
            self._all = " ".join(u[2] for u in self.units)
        return self._all

    def idf(self, t):
        return math.log((1 + len(self.units)) / (1 + self.df.get(t, 0))) + 1.0

    def best(self, sent, k=2):
        q = Counter(norm(t) for t in toks(sent))
        if not q:
            return []
        qmass = sum(self.idf(t) for t in q)
        scored = []
        for src, ln, text, c in self.units:
            ov = sum(self.idf(t) for t in q if t in c)
            if ov > 0:
                scored.append((ov / qmass, src, ln, text))
        scored.sort(reverse=True, key=lambda x: x[0])
        return scored[:k]


def build(folder):
    ix = Index()
    counts = {
        "career_bank": ix.add_file(career_bank(folder), "career-bank.md"),
        "jd": ix.add_file(os.path.join(folder, "jd-posting.txt"), "jd-posting.txt", verbatim_only=True),
        "company_research": ix.add_file(os.path.join(folder, "company-research.md"), "company-research.md"),
    }
    return ix, counts


def check(folder, draft, threshold=0.34):
    ix, counts = build(folder)
    out = []
    for s in sentences(read(draft)):
        flags = [(tag, why) for pat, tag, why in RISK if re.search(pat, s, re.I)]
        # A figure or an absence claim attached to a collective scope must be
        # sourced explicitly: overlap cannot see that the scope widened.
        if re.search(SCOPE_BREADTH, s, re.I) and (
                re.search(r"\b\d[\d,]*(\.\d+)?%?\b", s)
                or any(t == "ABSENCE-OR-FIRST" for t, _ in flags)):
            flags.append(("SCOPE-BREADTH", "a figure or absence claim attached to a collective scope - "
                          "confirm the source covers that whole scope, not one team inside it"))
        hits = ix.best(s)
        top = hits[0][0] if hits else 0.0
        tags = {t for t, _ in flags}
        # A figure or year must appear LITERALLY somewhere in the sources.
        literals = set(re.findall(r"\b(?:19|20)\d\d\b", s)) | set(re.findall(r"\b\d[\d,]{1,}\b", s))
        unmatched = sorted(l for l in literals if l not in ix.all_text())
        if tags & BLOCKING or unmatched:
            status = "UNSUPPORTED"
        elif top >= threshold:
            status = "SUPPORTED"
        else:
            status = "REVIEW"
        out.append({
            "sentence": s, "status": status, "score": round(top, 3),
            "flags": [{"tag": t, "why": w} for t, w in flags],
            "unmatched_literals": unmatched,
            "evidence": [{"source": h[1], "line": h[2], "text": h[3][:180], "score": round(h[0], 3)} for h in hits],
            "disposition": None,
        })
    return {"draft": os.path.basename(draft), "threshold": threshold, "corpora": counts, "sentences": out}


def main():
    ap = argparse.ArgumentParser(prog="ground.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("folder"); c.add_argument("--draft", required=True)
    c.add_argument("--threshold", type=float, default=0.34)
    c.add_argument("--out", default=None)
    a = ap.parse_args()
    folder = os.path.abspath(a.folder)
    res = check(folder, a.draft, a.threshold)
    dest = a.out or os.path.join(folder, "grounding.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    bad = [s for s in res["sentences"] if s["status"] == "UNSUPPORTED"]
    rev = [s for s in res["sentences"] if s["status"] == "REVIEW"]
    print(f"corpora: career-bank={res['corpora']['career_bank']} jd={res['corpora']['jd']} "
          f"company={res['corpora']['company_research']} lines")
    print(f"{len(res['sentences'])} sentences: {len(res['sentences']) - len(bad) - len(rev)} supported, "
          f"{len(rev)} review, {len(bad)} UNSUPPORTED")
    for s in bad + rev:
        print(f"\n  [{s['status']}] score={s['score']}\n    {s['sentence'][:150]}")
        for fl in s["flags"]:
            print(f"      !! {fl['tag']}: {fl['why']}")
        if s["unmatched_literals"]:
            print(f"      !! FIGURE NOT IN ANY SOURCE: {', '.join(s['unmatched_literals'])}")
        if s["evidence"]:
            e = s["evidence"][0]
            print(f"      best match ({e['score']}): {e['source']}:{e['line']} - {e['text'][:110]}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
