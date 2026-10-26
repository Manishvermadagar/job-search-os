#!/usr/bin/env python3
"""verify: application-verifier passed EACH answer, by name, after its last edit.

A verdict that does not name the file is a verdict on something else, and a PASS
written before the answer last changed covers bytes the verifier never saw.
"""
import os
from common import answers, folder_arg, finish, last_verdict, read

folder = folder_arg()
vp = os.path.join(folder, "verification.md")
problems = []
if not os.path.exists(vp):
    finish(["verification.md is missing - run application-verifier on every answer"], "")
text = read(vp)
a = answers(folder)
for key, rel, path in a:
    name = rel.replace("\\", "/")
    v = last_verdict(text, name, r"VERDICT:\s*(PASS|FAIL)")
    if v is None:
        problems.append(f"{rel}: verification.md never names it with a verdict (use a heading '## {name}')")
    elif v != "PASS":
        problems.append(f"{rel}: the latest verdict is {v}. Repair by failure class and verify again.")
    elif os.path.exists(path) and os.path.getmtime(path) > os.path.getmtime(vp) + 1:
        problems.append(f"{rel}: changed after verification.md was last written - verify the new text")
finish(problems, f"verifier PASS on all {len(a)} answer(s), each by name")
