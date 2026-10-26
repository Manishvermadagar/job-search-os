#!/usr/bin/env python3
"""evidence_pack: everything a reviewer needs is present, and hashed.

A reviewer can only review what it is given. If the pack is incomplete or stale,
it returns a confident verdict on the wrong thing and nothing catches it. This
checks the pack is complete and writes evidence-pack.json with a hash per file,
so a later review can be matched to the exact bytes it saw.
"""
import hashlib, json, os
from common import answers, career_bank, finish, folder_arg, intended, nonempty, resolve

folder = folder_arg()


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


problems, pack = [], {}
for key, rel, path in answers(folder):
    if not nonempty(path):
        problems.append(f"{key}: answer missing or empty -> {rel}")
    else:
        pack[f"answer:{rel}"] = {"path": rel, "sha256": sha(path)}
for key, ch in intended(folder).items():
    c = ch.get("contains") or {}
    for r in [c.get("resume")] + list(c.get("attachments") or []):
        if not r:
            continue
        p = resolve(folder, r)
        if not os.path.exists(p):
            problems.append(f"{key}: declared file does not exist -> {r}")
        else:
            pack[f"file:{r}"] = {"path": str(r), "sha256": sha(p)}

cb = career_bank(folder)
if not nonempty(cb):
    problems.append("the career bank (the fact ceiling) was not found - no claim can be checked without it")
else:
    pack["ceiling:career-bank.md"] = {"path": os.path.basename(cb), "sha256": sha(cb)}
for req, why in [("jd-posting.txt", "question fit cannot be judged without the posting"),
                 ("company-research.md", "employer claims cannot be checked without it")]:
    p = os.path.join(folder, req)
    if not nonempty(p):
        problems.append(f"{req} missing or empty - {why}")
    else:
        pack[f"context:{req}"] = {"path": req, "sha256": sha(p)}

with open(os.path.join(folder, "evidence-pack.json"), "w", encoding="utf-8") as f:
    json.dump(pack, f, indent=2)
finish(problems, f"evidence pack complete: {len(pack)} file(s) hashed -> evidence-pack.json",
       header="EVIDENCE PACK INCOMPLETE")
