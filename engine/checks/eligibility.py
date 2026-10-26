#!/usr/bin/env python3
"""eligibility: PROCEED with a compensation verdict taken from salary-thresholds.md.

SKIP is a valid outcome but not a pass: the run ends with 'apply.py abort'.
"""
import os, re
from common import folder_arg, finish, nonempty, read

folder = folder_arg()
p = os.path.join(folder, "eligibility.md")
problems = []
if not nonempty(p):
    finish(["eligibility.md is missing or empty"], "")
t = read(p)
v = re.findall(r"VERDICT:\s*(PROCEED|SKIP)", t, re.I)
c = re.findall(r"COMPENSATION:\s*(CLEARS|BELOW|UNKNOWN)", t, re.I)
if not v:
    problems.append("no 'VERDICT: PROCEED' or 'VERDICT: SKIP' line")
elif v[-1].upper() == "SKIP":
    problems.append("VERDICT: SKIP - end this run with: apply.py abort <folder> --reason '<the quoted bar>'")
if not c:
    problems.append("no 'COMPENSATION: CLEARS | BELOW | UNKNOWN' line. Take it from "
                    "resume-data/salary-thresholds.md; UNKNOWN is allowed, a guessed figure is not.")
elif c[-1].upper() == "BELOW" and not re.search(r"USER OVERRIDE:", t):
    problems.append("COMPENSATION: BELOW with PROCEED needs a 'USER OVERRIDE:' line recording the user's own decision")
finish(problems, f"eligibility: PROCEED, compensation {c[-1].upper() if c else '?'}")
