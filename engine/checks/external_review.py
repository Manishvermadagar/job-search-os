#!/usr/bin/env python3
"""external_review: a second opinion that covers the final files, or a recorded skip.

The external review is optional. Skipping it silently is not: either
review/review-round-<n>.md names every answer and the resume PDF with a final
'VERDICT: READY TO SUBMIT', or external-review-skipped.md says why not.

A review written before a file last changed covers bytes the reviewer never saw.
"""
import glob, os, re
from common import answers, finish, folder_arg, intended, last_verdict, nonempty, read, resolve

folder = folder_arg()
skip = os.path.join(folder, "external-review-skipped.md")
rounds = sorted(glob.glob(os.path.join(folder, "review", "review-round-*.md")),
                key=lambda p: int(re.search(r"(\d+)", os.path.basename(p)).group(1)))

if not rounds:
    if nonempty(skip) and re.search(r"^REASON:\s*\S", read(skip), re.M):
        finish([], "external review skipped by recorded decision: " +
               re.search(r"^REASON:\s*(.+)$", read(skip), re.M).group(1)[:100])
    finish(["no review/review-round-*.md and no external-review-skipped.md with a 'REASON:' line. "
            "Run external-reviewer, or record why it was skipped."], "")

targets = [(rel, path) for _, rel, path in answers(folder)]
for key, ch in intended(folder).items():
    r = (ch.get("contains") or {}).get("resume")
    if r and str(r).lower().endswith(".pdf"):
        targets.append((str(r), resolve(folder, r)))

latest = rounds[-1]
text = read(latest)
problems = []
for rel, path in targets:
    name = os.path.basename(rel)
    v = last_verdict(text, name, r"VERDICT:\s*(READY TO SUBMIT|NOT READY)")
    if v is None:
        problems.append(f"{rel}: the latest round ({os.path.basename(latest)}) does not name it with a verdict")
    elif v != "READY TO SUBMIT":
        problems.append(f"{rel}: latest external verdict is {v}")
    elif os.path.exists(path) and os.path.getmtime(path) > os.path.getmtime(latest) + 1:
        problems.append(f"{rel}: changed after {os.path.basename(latest)} - send the new version for review")
finish(problems, f"external review READY TO SUBMIT on {len(targets)} file(s) in {os.path.basename(latest)}")
