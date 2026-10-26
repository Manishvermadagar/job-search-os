#!/usr/bin/env python3
"""
Deterministic job-description keyword tiering. Split out of
resume-content-optimizer so both that skill and resume-profile-manager can
call one shared, auditable tiering instead of each re-deriving keywords by
LLM guess. Tiering is by raw frequency in the JD text -- a dumb, reproducible
rule on purpose (see resume-analyser's SKILL.md for why "the LLM invents a
plausible-looking number" is the failure mode this whole resume-skill set is
built to avoid).

Usage:
  python3 parse_jd.py <job_description.txt> [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

STOPWORDS = set("""
a an the and or but if of to in on for with at by from as is are was were be
been being this that these those it its your you we our i my their they he
she his her will shall can may might must should would about into over
under between within through per etc a's able also across after again all
almost along already although always am among any anyone anything anyway
""".split())


def tokenize(text):
    raw = re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{1,}", text)
    return [w.lower() for w in (re.sub(r"[./-]+$", "", w) for w in raw) if w]


def tier_keywords(jd_text):
    tokens = [t for t in tokenize(jd_text) if t not in STOPWORDS and len(t) > 2]
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    tier1 = sorted([t for t, c in freq.items() if c >= 3])
    tier2 = sorted([t for t, c in freq.items() if c == 2])
    # Tier 3: single-mention terms that look like a named tool/tech/proper
    # noun in the ORIGINAL text (capitalized mid-sentence, not sentence-start)
    # -- a real, inspectable rule, not an LLM guessing importance.
    tier3 = set()
    for line in jd_text.split("\n"):
        words = line.split()
        for i, w in enumerate(words):
            clean = re.sub(r"[^A-Za-z0-9+#.-]", "", w)
            if not clean:
                continue
            if i > 0 and clean[:1].isupper() and clean.lower() not in STOPWORDS:
                low = clean.lower()
                if freq.get(low, 0) == 1:
                    tier3.add(low)
    tier3 = sorted(tier3 - set(tier1) - set(tier2))
    return {"tier1_frequency_3_plus": tier1, "tier2_frequency_2": tier2,
            "tier3_single_mention_named_terms": tier3}


REQUIRED_MARKERS = re.compile(r"required|must have|minimum qualifications|you have", re.IGNORECASE)
PREFERRED_MARKERS = re.compile(r"preferred|nice to have|bonus|a plus", re.IGNORECASE)


def split_requirement_lines(jd_text):
    """Bucket bullet/line-level requirements by which section marker they sit
    under -- a coarse heuristic (JDs aren't structured consistently), so this
    is reported as a starting point for Claude to sanity-check, not a final
    answer."""
    lines = [l.strip() for l in jd_text.split("\n") if l.strip()]
    required, preferred, mode = [], [], "required"
    for line in lines:
        if REQUIRED_MARKERS.search(line) and len(line) < 80:
            mode = "required"
            continue
        if PREFERRED_MARKERS.search(line) and len(line) < 80:
            mode = "preferred"
            continue
        if re.match(r"^[-*•]\s+", line):
            (required if mode == "required" else preferred).append(re.sub(r"^[-*•]\s+", "", line))
    return {"required_lines": required, "preferred_lines": preferred}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jd", help="Job description text file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    jd_text = Path(args.jd).read_text(encoding="utf-8")
    report = {**tier_keywords(jd_text), **split_requirement_lines(jd_text)}

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("=== JD keyword tiers (computed by frequency, not guessed) ===")
    print(f"Tier 1 (mentioned 3+ times -- review for role relevance and candidate support): {', '.join(report['tier1_frequency_3_plus']) or '(none)'}")
    print(f"Tier 2 (mentioned 2x -- should appear if genuinely true): {', '.join(report['tier2_frequency_2']) or '(none)'}")
    print(f"Tier 3 (single-mention named tools/terms -- place if relevant): {', '.join(report['tier3_single_mention_named_terms']) or '(none)'}")
    print(f"\nBulleted lines under a 'required'-style heading: {len(report['required_lines'])}")
    print(f"Bulleted lines under a 'preferred'-style heading: {len(report['preferred_lines'])}")
    print("(Heading detection is a coarse heuristic -- verify against the actual JD structure before treating a line as required vs. preferred.)")


if __name__ == "__main__":
    sys.exit(main())
