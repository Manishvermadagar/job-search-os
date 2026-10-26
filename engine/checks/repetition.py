#!/usr/bin/env python3
"""repetition: no answer is reheated from another application.

Compares each answer's six-word runs against the answers of every other
application folder (sibling folders of this one) whose run reached 'ready'.
Contact lines and signatures are ignored: a signature repeating is correct.
"""
import json, os, re
from common import answers, folder_arg, finish, read, resolve

N = 6
CONTACT = re.compile(r"@|\+\d{1,3}[-\s]?\d{6,}|linkedin\.com|github\.com|^\s*DEMO\b", re.I)

folder = folder_arg()


def shingles(text):
    lines = [ln for ln in text.splitlines() if not CONTACT.search(ln)]
    words = re.findall(r"[a-z0-9']+", " ".join(lines).lower())
    return {" ".join(words[i:i + N]) for i in range(len(words) - N + 1)}


def finished_answers(other):
    st_p = os.path.join(other, "run-state.json")
    ch_p = os.path.join(other, "channels.json")
    if not (os.path.exists(st_p) and os.path.exists(ch_p)):
        return []
    try:
        st, ch = json.load(open(st_p, encoding="utf-8")), json.load(open(ch_p, encoding="utf-8"))
    except ValueError:
        return []
    if st.get("aborted") or any(n["state"] != "done" for n in st["nodes"].values()):
        return []
    out = []
    for c in ch.values():
        if (c or {}).get("status") == "INTENDED":
            for a in ((c.get("contains") or {}).get("answers") or []):
                p = resolve(other, a)
                if os.path.exists(p):
                    out.append((os.path.basename(other), str(a), p))
    return out


parent = os.path.dirname(folder)
prior = []
for name in sorted(os.listdir(parent)):
    other = os.path.join(parent, name)
    if os.path.isdir(other) and os.path.normcase(other) != os.path.normcase(folder):
        prior += [(app, rel, shingles(read(p))) for app, rel, p in finished_answers(other)]

problems = []
mine = answers(folder)
for key, rel, path in mine:
    s = shingles(read(path))
    for app, orel, os_ in prior:
        shared = sorted(s & os_)
        if shared:
            problems.append(f"{rel} shares {len(shared)} six-word run(s) with {app}/{orel}, e.g. \"{shared[0]}\". "
                            f"Change the evidence or the angle, not the wording.")
finish(problems, f"repetition clean: {len(mine)} answer(s) checked against {len(prior)} finished answer(s)")
