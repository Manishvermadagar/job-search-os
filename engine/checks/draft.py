#!/usr/bin/env python3
"""draft: every answer an INTENDED channel sends exists and is not empty."""
from common import answers, folder_arg, finish, nonempty

folder = folder_arg()
a = answers(folder)
problems = [f"{k}: {rel} is missing or empty" for k, rel, path in a if not nonempty(path)]
if not a:
    problems.append("no answers listed by any INTENDED channel")
finish(problems, f"{len(a)} answer file(s) drafted")
