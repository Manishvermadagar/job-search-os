#!/usr/bin/env python3
"""briefs: each answer has a question brief, an argument brief with rejected
angles, and company research exists."""
import os, re
from common import answer_id, answers, folder_arg, finish, nonempty, read

folder = folder_arg()
problems = []
ids = sorted({answer_id(rel) for _, rel, _ in answers(folder)})
if not ids:
    problems.append("no answers listed by any INTENDED channel")
for i in ids:
    q = os.path.join(folder, "briefs", f"{i}-question-brief.md")
    a = os.path.join(folder, "briefs", f"{i}-argument-brief.md")
    if not nonempty(q):
        problems.append(f"{i}: briefs/{i}-question-brief.md missing (question-interpreter)")
    if not nonempty(a):
        problems.append(f"{i}: briefs/{i}-argument-brief.md missing (application-strategist)")
    elif not re.search(r"\brejected\b", read(a), re.I):
        problems.append(f"{i}: the argument brief records no REJECTED angle. One angle means the first idea was taken.")
if not nonempty(os.path.join(folder, "company-research.md")):
    problems.append("company-research.md is missing or empty")
finish(problems, f"briefs present for {len(ids)} answer(s), company research present")
