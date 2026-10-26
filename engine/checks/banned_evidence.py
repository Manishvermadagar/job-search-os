#!/usr/bin/env python3
"""banned_evidence: evidence this application's argument brief excluded stays out
of EVERYTHING that leaves, including the tailored resume.

A ban written for the answers does not reach the resume on its own: the resume is
built from a different file and the grounder never reads it. banned-evidence.txt
holds one regular expression per line, in two sections:

  [all]          banned for THIS application everywhere, resume included (default)
  [bodies-only]  banned from written answers only - e.g. a figure already spent as
                 the centre of another application's argument. A generic resume is
                 the same career sent to everyone, so the fact may stay there.

No banned-evidence.txt means nothing is excluded, and the check passes.
"""
import os, re
from common import extract_text, finish, folder_arg, intended, read, resolve

folder = folder_arg()
bp = os.path.join(folder, "banned-evidence.txt")
if not os.path.exists(bp):
    finish([], "no banned-evidence.txt - nothing excluded for this application")

pats, section = {"all": [], "bodies-only": []}, "all"
for line in read(bp).splitlines():
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    m = re.fullmatch(r"\[(all|bodies-only)\]", line)
    if m:
        section = m.group(1)
    else:
        pats[section].append(line)

targets = []
for key, ch in intended(folder).items():
    c = ch.get("contains") or {}
    targets += [(f"{key}:answer", a) for a in (c.get("answers") or [])]
    if c.get("resume"):
        targets.append((f"{key}:resume", c["resume"]))

problems = []
for label, rel in targets:
    path = resolve(folder, rel)
    text = extract_text(path) if os.path.exists(path) else None
    if text is None:
        problems.append(f"{label}: cannot read {rel}"); continue
    flat = re.sub(r"\s+", " ", text)
    applicable = pats["all"] + ([] if label.endswith(":resume") else pats["bodies-only"])
    for p in applicable:
        if re.search(p, flat, re.I):
            problems.append(f"{label} ({rel}) contains banned evidence /{p}/. Replace it with different "
                            f"supported evidence; rewording keeps the same evidence.")
finish(problems, f"banned evidence absent from {len(targets)} artifact(s)", header="BANNED EVIDENCE PRESENT")
