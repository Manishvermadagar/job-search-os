#!/usr/bin/env python3
"""jd_capture: the posting is saved verbatim, and analysed against the career bank."""
import os, re
from common import folder_arg, finish, nonempty, read

folder = folder_arg()
problems = []
jd = os.path.join(folder, "jd-posting.txt")
if not nonempty(jd):
    problems.append("jd-posting.txt is missing or empty")
elif len(re.findall(r"\w+", read(jd))) < 40:
    problems.append("jd-posting.txt has under 40 words - that is a summary, not the verbatim posting")
if not nonempty(os.path.join(folder, "jd-analysis.md")):
    problems.append("jd-analysis.md is missing or empty (requirements marked MET / PARTIAL / GAP)")
finish(problems, "posting captured verbatim and analysed")
