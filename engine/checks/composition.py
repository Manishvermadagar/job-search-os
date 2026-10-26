#!/usr/bin/env python3
"""composition: does each intended channel CONTAIN what it must?

Checks of the steps taken say nothing about what the deliverable holds. An
application email can pass every writing check and still go out with no resume.
An application is incomplete unless the recipient can, from what they receive
alone, see who is applying, read why, and get everything the posting asked for.
"""
import os, re
from common import finish, folder_arg, intended, load_json, nonempty, resolve

folder = folder_arg()
req = (load_json(folder, "required-artifacts.json") or {}).get("items") or []
problems = []


def identity(it):
    """Stable identity for a required item, so a record is matched on meaning,
    not on an echo of the whole JSON object."""
    if not isinstance(it, dict):
        return str(it).strip().lower()
    name = str(it.get("artifact", "")).strip().lower()
    qid = str(it.get("question_id", "")).strip()
    return f"{name}#{qid}" if qid else name


chs = intended(folder)
if not chs:
    problems.append("no channel is INTENDED - nothing would be submitted")
for key, ch in chs.items():
    c = ch.get("contains") or {}
    # who is applying
    if "email" in key.lower():
        resumes = [a for a in (c.get("attachments") or [])
                   if str(a) == str(c.get("resume") or "") or re.search(r"resume|\bcv\b", str(a), re.I)]
        if not resumes:
            problems.append(f"{key}: NO RESUME ATTACHED. An email without a resume does not show who is applying.")
        for a in resumes:
            if not nonempty(resolve(folder, a)):
                problems.append(f"{key}: attachment missing or empty: {a}")
    elif not c.get("resume"):
        problems.append(f"{key}: no resume recorded. Record the file you will upload, and check the "
                        f"platform actually holds it rather than assuming it does.")
    # why they are applying
    for a in (c.get("answers") or []):
        if not nonempty(resolve(folder, a)):
            problems.append(f"{key}: answer missing or empty: {a}")
    # everything the posting asked for
    got = {identity(g) for g in (c.get("posting_artifacts") or [])}
    for item in req:
        ch_of = str(item.get("channel", "all")).strip().lower() if isinstance(item, dict) else "all"
        if ch_of not in ("all", "", key.lower()):
            continue
        if identity(item) not in got:
            problems.append(f"{key}: the posting requires '{identity(item)}' and it is not recorded in "
                            f"contains.posting_artifacts (recorded: {sorted(got) or 'nothing'})")
finish(problems, "composition OK - every intended channel carries answers, resume and posting-required artifacts",
       header="COMPOSITION FAILED")
