#!/usr/bin/env python3
"""
Filter/rank career-bank bullets against a target profile's priority tags.
Real, auditable selection logic -- not an LLM re-reading the whole career
history and guessing which bullets "feel relevant" every time a resume is
built for a new profile.

Career bank format (see references/career-bank-format.md):
  ## Company — Title | Dates
  tags: tag-one, tag-two
  - Bullet text [tags: tag-a, tag-b]

Profile format (see references/profile-format.md):
  priority_tags: tag-one, tag-b, tag-c

Usage:
  python3 select_for_profile.py <career-bank.md> <profile.md> [--json]
"""
import argparse
import json
import re
import sys
from pathlib import Path


def parse_profile_tags(profile_text):
    m = re.search(r"^priority_tags:\s*(.+)$", profile_text, re.MULTILINE)
    if not m:
        return []
    return [t.strip().lower() for t in m.group(1).split(",") if t.strip()]


def parse_career_bank(text):
    """Returns a list of {role, dates, role_tags, bullet, bullet_tags}."""
    entries = []
    role_header = re.compile(r"^##\s+(.+?)\s*\|\s*(.+)$")
    tags_line = re.compile(r"^tags:\s*(.+)$", re.IGNORECASE)
    bullet_line = re.compile(r"^[-*]\s+(.+)$")

    current_role, current_dates, current_role_tags = None, None, []
    for line in text.split("\n"):
        stripped = line.strip()
        h = role_header.match(stripped)
        if h:
            current_role, current_dates = h.group(1), h.group(2)
            current_role_tags = []
            continue
        if stripped.startswith("## "):
            current_role, current_dates, current_role_tags = None, None, []
            continue
        t = tags_line.match(stripped)
        if t and current_role:
            current_role_tags = [x.strip().lower() for x in t.group(1).split(",") if x.strip()]
            continue
        b = bullet_line.match(stripped)
        if b and current_role:
            body = b.group(1)
            bm = re.search(r"\[tags:\s*(.+?)\]", body)
            bullet_tags = [x.strip().lower() for x in bm.group(1).split(",")] if bm else []
            body_clean = re.sub(r"\s*\[tags:.+?\]\s*$", "", body).strip()
            entries.append({
                "role": current_role, "dates": current_dates,
                "role_tags": current_role_tags, "bullet": body_clean,
                "bullet_tags": bullet_tags,
            })
    return entries


def rank(entries, priority_tags):
    priority_set = set(priority_tags)
    scored = []
    for e in entries:
        all_tags = set(e["role_tags"]) | set(e["bullet_tags"])
        overlap = all_tags & priority_set
        scored.append({**e, "match_score": len(overlap), "matched_tags": sorted(overlap)})
    scored.sort(key=lambda x: x["match_score"], reverse=True)
    return scored


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("career_bank", help="career-bank.md path")
    parser.add_argument("profile", help="profile .md path (must have a priority_tags: line)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--min-score", type=int, default=0, help="drop bullets scoring below this")
    args = parser.parse_args()

    bank_text = Path(args.career_bank).read_text(encoding="utf-8")
    profile_text = Path(args.profile).read_text(encoding="utf-8")

    priority_tags = parse_profile_tags(profile_text)
    if not priority_tags:
        print("No `priority_tags:` line found in the profile file -- nothing to rank against.", file=sys.stderr)
        sys.exit(1)

    entries = parse_career_bank(bank_text)
    ranked = [e for e in rank(entries, priority_tags) if e["match_score"] >= args.min_score]

    if args.json:
        print(json.dumps({"priority_tags": priority_tags, "ranked_bullets": ranked}, indent=2))
        return

    print(f"Priority tags for this profile: {', '.join(priority_tags)}\n")
    zero_score = [e for e in ranked if e["match_score"] == 0]
    for e in ranked:
        if e["match_score"] > 0:
            print(f"[{e['match_score']}] ({e['role']}) {e['bullet']}  -- matched: {', '.join(e['matched_tags'])}")
    if zero_score:
        print(f"\n{len(zero_score)} bullets matched none of this profile's priority tags (omit or re-tag if relevant):")
        for e in zero_score:
            print(f"  ({e['role']}) {e['bullet']}")


if __name__ == "__main__":
    sys.exit(main())
