#!/usr/bin/env python3
"""
Deterministic, code-backed resume checks: banned-phrase scan, keyword overlap
against a job description, and structural checks (bullets, metrics, sections,
length). Exists because every public "ATS score" skill surveyed for this
project (dabydat/resume-builder-skill, ARPeeketi/claude-resume-kit,
SankaiAI/ats-optimized-resume-agent-skill, Paramchoudhary/ResumeSkills,
nipungakkhar/ats_resume_optimizer, erichowens/cv-creator) turned out to be an
LLM narrating a number into a template, not a computed score. Everything in
this script is a real count -- no LLM judgment. The qualitative critique
(5-persona review) is a separate step Claude runs on top of this output; see
SKILL.md.

Usage:
  python3 analyze_resume.py <resume.md> [--jd job_description.txt]
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Sourced from ARPeeketi/claude-resume-kit's ai_fingerprint_rules.md and
# SankaiAI/ats-optimized-resume-agent-skill's BANNED_PHRASES (renderer/src/
# validation/validate_output.py) -- merged and deduplicated. SankaiAI only
# warns on these; we hard-fail, since a warning nobody reads doesn't stop
# a banned phrase from shipping.
BANNED_WORDS = [
    "delve", "tapestry", "multifaceted", "pivotal", "leverage", "utilize",
    "spearhead", "synergy", "robust", "seamless", "cutting-edge",
    "game-changer", "paradigm", "holistic", "bespoke", "unparalleled",
]
BANNED_PHRASES = [
    "responsible for", "passionate about", "results-driven",
    "proven track record", "team player", "detail-oriented",
    "hard worker", "go-getter", "think outside the box",
    "i am uniquely positioned to", "it's not just", "in today's fast-paced",
]

# Resumes omit the subject entirely ("Directed X", not "He directed X") --
# third-person pronouns are a structural convention violation, not a
# style preference, and are 100% mechanically detectable, so this is a
# code check, not something left to judgment.
THIRD_PERSON_PRONOUNS = [
    "he", "him", "his", "himself", "she", "her", "hers", "herself",
]

WEAK_BULLET_STARTS = [
    "responsible for", "helped", "worked on", "assisted with",
    "involved in", "participated in", "duties included",
]

SECTION_HEADERS = {
    "experience": r"(professional )?experience|work history|employment",
    "education": r"education",
    "skills": r"(technical )?skills|core competencies",
    "summary": r"summary|profile|objective",
}

STOPWORDS = set("""
a an the and or but if of to in on for with at by from as is are was were be
been being this that these those it its your you we our i my their they he
she his her will shall can may might must should would about into over
under between within through per etc
""".split())


def read_text(path):
    return Path(path).read_text(encoding="utf-8")


def inflections(term):
    """leverage -> {leverage, leveraged, leveraging, leverages}; handles the
    silent-e drop before -ing that a bare suffix regex gets wrong."""
    forms = {term}
    if term.endswith("e"):
        forms.add(term + "d")
        forms.add(term[:-1] + "ing")
        forms.add(term + "s")
    else:
        forms.add(term + "ed")
        forms.add(term + "ing")
        forms.add(term + "s")
    return forms


def find_banned(text):
    lines = text.split("\n")
    hits = []
    for term_list, kind in [(BANNED_WORDS, "word"), (BANNED_PHRASES, "phrase")]:
        for term in term_list:
            if " " in term:
                forms = {term}  # multi-word phrases: match as-is, no inflection
            else:
                forms = inflections(term)
            pattern = re.compile(r"\b(?:" + "|".join(re.escape(f) for f in forms) + r")\b", re.IGNORECASE)
            for lineno, line in enumerate(lines, 1):
                if pattern.search(line):
                    hits.append({"type": kind, "term": term, "line": lineno, "text": line.strip()})
    return hits


def find_pronouns(text):
    lines = text.split("\n")
    pattern = re.compile(r"\b(?:" + "|".join(THIRD_PERSON_PRONOUNS) + r")\b", re.IGNORECASE)
    hits = []
    for lineno, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            hits.append({"term": m.group(0).lower(), "line": lineno, "text": line.strip()})
    return hits


def tokenize(text):
    raw = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{1,}", text)
    # Strip trailing punctuation a sentence boundary leaves attached
    # ("required." -> "required") without breaking real tokens like "A/B" or "C++".
    return [w.lower() for w in (re.sub(r"[./-]+$", "", w) for w in raw) if w]


def keyword_overlap(resume_text, jd_text):
    jd_tokens = [t for t in tokenize(jd_text) if t not in STOPWORDS and len(t) > 2]
    freq = {}
    for t in jd_tokens:
        freq[t] = freq.get(t, 0) + 1
    # Keywords = JD terms appearing 2+ times, or capitalized multi-word terms
    # (proper nouns / tech terms) in the original JD -- a real, inspectable
    # rule, not an LLM guessing which words "matter".
    candidates = {t for t, c in freq.items() if c >= 2}
    resume_tokens = set(tokenize(resume_text))
    matched = sorted(t for t in candidates if t in resume_tokens)
    missing = sorted(t for t in candidates if t not in resume_tokens)
    pct = round(100 * len(matched) / len(candidates), 1) if candidates else None
    return {"total_keywords": len(candidates), "matched": matched, "missing": missing, "match_pct": pct}


def bullet_lines(text):
    return [l.strip() for l in text.split("\n") if re.match(r"^\s*[-*•]\s+", l)]


def structural_checks(text):
    bullets = bullet_lines(text)
    weak = []
    no_metric = []
    for b in bullets:
        body = re.sub(r"^[-*•]\s+", "", b).strip()
        if any(body.lower().startswith(w) for w in WEAK_BULLET_STARTS):
            weak.append(body)
        if not re.search(r"\d", body):
            no_metric.append(body)
    words = tokenize(text)
    sections_found = {
        name: bool(re.search(pattern, text, re.IGNORECASE))
        for name, pattern in SECTION_HEADERS.items()
    }
    # "summary" is a special case: this project's own drafts increasingly use
    # a role-title headline ("## Operations Leader", "## Customer Success
    # Manager") as the summary section's heading instead of the literal word
    # "Summary" -- the plain regex above only ever matched that pattern by
    # coincidence (e.g. the word "objective" turning up in an unrelated
    # bullet), which is not a real check. Structurally, this project's
    # resumes/CVs always open with exactly one "## " section before the
    # "## Experience"/"## Professional Experience" section -- if that
    # structural summary block exists, count it even when its heading text
    # doesn't literally say "summary".
    if not sections_found["summary"]:
        h2_lines = re.findall(r"^##\s+(.*)$", text, re.MULTILINE)
        if h2_lines:
            first_heading = h2_lines[0].strip().lower()
            if not re.search(SECTION_HEADERS["experience"], first_heading, re.IGNORECASE):
                sections_found["summary"] = True
    return {
        "word_count": len(words),
        "est_pages": round(len(words) / 550, 2),
        "bullet_count": len(bullets),
        "weak_verb_bullets": weak,
        "bullets_without_metric": no_metric,
        "pct_bullets_with_metric": round(
            100 * (len(bullets) - len(no_metric)) / len(bullets), 1
        ) if bullets else None,
        "sections_found": sections_found,
        "missing_sections": [k for k, v in sections_found.items() if not v],
    }


def compute_ats_score(report, doctype):
    """Rubric-based ATS pass-likelihood score, 0-100, every component a direct
    function of the computed checks above -- no LLM judgment enters this
    number. This is a "how parseable/keyword-hygienic is this document" score,
    not a "will you get the job" score; keep it labeled that way in output."""
    s = report["structure"]
    bp = report["banned_phrases"]
    ph = report["pronoun_hits"]

    sections_score = 25 * (4 - len(s["missing_sections"])) / 4
    banned_score = max(0, 25 - 5 * (len(bp) + len(ph)))
    metric_score = 25 * (s["pct_bullets_with_metric"] or 0) / 100
    weak_score = max(0, 15 - 3 * len(s["weak_verb_bullets"]))

    if doctype == "cv":
        # CVs aren't penalized for length -- real depth is the point.
        length_score = 10 if s["word_count"] >= 300 else 10 * s["word_count"] / 300
    else:
        # Resume: full points inside 1.7-2.15 pages, linearly scaled outside.
        # Default: resumes target ~2 pages, not ~1 -- see ats-formatting-rules.md "Page length".
        pages = s["est_pages"]
        if 1.7 <= pages <= 2.15:
            length_score = 10
        elif pages < 1.7:
            length_score = 10 * pages / 1.7
        else:
            length_score = max(0, 10 - 6 * (pages - 2.15))

    breakdown = {
        "sections_present (/25)": round(sections_score, 1),
        "banned_phrases (/25)": round(banned_score, 1),
        "bullets_with_metric (/25)": round(metric_score, 1),
        "no_weak_verbs (/15)": round(weak_score, 1),
        "length_fit (/10)": round(length_score, 1),
    }
    total = round(sum(breakdown.values()), 1)
    return {"total": total, "breakdown": breakdown}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resume", help="Resume file (Markdown or plain text)")
    parser.add_argument("--jd", help="Job description file to compute keyword overlap against")
    parser.add_argument("--doctype", choices=["resume", "cv"], default="resume",
                         help="Scoring profile: 'resume' penalizes length outside ~2 pages (project override, see ats-formatting-rules.md), 'cv' does not")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON instead of a formatted report")
    args = parser.parse_args()

    resume_text = read_text(args.resume)
    report = {
        "banned_phrases": find_banned(resume_text),
        "pronoun_hits": find_pronouns(resume_text),
        "structure": structural_checks(resume_text),
    }
    if args.jd:
        report["keyword_overlap"] = keyword_overlap(resume_text, read_text(args.jd))
    report["ats_score"] = compute_ats_score(report, args.doctype)

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== Deterministic Resume Checks (code-computed, not LLM-estimated) ===\n")
    bp = report["banned_phrases"]
    print(f"Banned words/phrases: {len(bp)} found" + (" -- FAIL" if bp else " -- clean"))
    for h in bp:
        print(f"  line {h['line']}: \"{h['term']}\" in: {h['text']}")

    ph = report["pronoun_hits"]
    print(f"\nThird-person pronouns (he/his/she/her/etc.): {len(ph)} found" +
          (" -- FAIL (resumes omit the subject entirely, never use he/his/she/her)" if ph else " -- clean"))
    for h in ph:
        print(f"  line {h['line']}: \"{h['term']}\" in: {h['text']}")

    s = report["structure"]
    print(f"\nWord count: {s['word_count']}  (~{s['est_pages']} pages at 550 words/page)")
    print(f"Bullets: {s['bullet_count']}, "
          f"{s['pct_bullets_with_metric']}% contain a number" if s['bullet_count'] else "\nBullets: 0")
    if s["weak_verb_bullets"]:
        print(f"  {len(s['weak_verb_bullets'])} bullets start with a weak verb (Responsible for / Helped / etc.):")
        for b in s["weak_verb_bullets"][:10]:
            print(f"    - {b}")
    if s["missing_sections"]:
        print(f"  Missing expected sections: {', '.join(s['missing_sections'])}")

    if "keyword_overlap" in report:
        ko = report["keyword_overlap"]
        print(f"\nJD keyword overlap: {ko['match_pct']}% ({len(ko['matched'])}/{ko['total_keywords']})")
        if ko["missing"]:
            print(f"  Missing JD keywords: {', '.join(ko['missing'][:25])}")

    ats = report["ats_score"]
    print(f"\n=== ATS score (doctype={args.doctype}): {ats['total']}/100 ===")
    print("(Parseability/keyword-hygiene score -- NOT a 'will you get the job' score. Breakdown:)")
    for k, v in ats["breakdown"].items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
