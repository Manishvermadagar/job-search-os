#!/usr/bin/env python3
"""ground: RUN the grounder over every answer; never accept a hand-written result.

A check that only asked for grounding.json to exist would pass an empty file.
This re-runs engine/ground.py every time, carries forward dispositions already
recorded for unchanged sentences, and requires one on every UNSUPPORTED sentence.
"""
import json, os, sys
from common import ENGINE, answer_id, answers, fail_now, folder_arg, finish

sys.path.insert(0, ENGINE)
import ground as G  # noqa: E402

DISPOSITIONS = ("SOURCE:", "RHETORICAL", "CUT")

folder = folder_arg()
a = answers(folder)
if not a:
    fail_now(["no answers listed by any INTENDED channel"])
os.makedirs(os.path.join(folder, "grounding"), exist_ok=True)

problems = []
for key, rel, path in a:
    if not os.path.exists(path):
        problems.append(f"{rel}: file missing"); continue
    out = os.path.join(folder, "grounding", answer_id(rel) + ".json")
    prior = {}
    if os.path.exists(out):
        try:
            prior = {s["sentence"]: s["disposition"] for s in json.load(open(out, encoding="utf-8"))["sentences"]
                     if s.get("disposition")}
        except (ValueError, KeyError):
            pass
    res = G.check(folder, path)
    for s in res["sentences"]:
        if s["sentence"] in prior:
            s["disposition"] = prior[s["sentence"]]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    uns = [s for s in res["sentences"] if s["status"] == "UNSUPPORTED"]
    for s in uns:
        d = str(s.get("disposition") or "")
        if not d.upper().startswith(DISPOSITIONS):
            tags = ", ".join(f["tag"] for f in s["flags"]) or "no source"
            lit = f"; figure not in any source: {', '.join(s['unmatched_literals'])}" if s["unmatched_literals"] else ""
            problems.append(f"{rel}: UNSUPPORTED [{tags}{lit}] \"{s['sentence'][:110]}\"")
        elif d.upper() == "CUT":
            problems.append(f"{rel}: marked CUT but still in the answer: \"{s['sentence'][:110]}\"")
    rev = [s for s in res["sentences"] if s["status"] == "REVIEW"]
    print(f"{rel}: {len(res['sentences'])} sentences, {len(uns)} unsupported, {len(rev)} review "
          f"-> grounding/{answer_id(rel)}.json")
    for s in rev:
        print(f"    review (weak support, verifier must check): \"{s['sentence'][:100]}\"")

if problems:
    problems.append('Record a disposition per sentence in grounding/<id>.json: '
                    '"SOURCE:career-bank.md:<line>" | "RHETORICAL" | "CUT" (then remove the sentence).')
finish(problems, "grounding OK - the grounder ran and every unsupported sentence is answered",
       header="GROUNDING FAILED")
