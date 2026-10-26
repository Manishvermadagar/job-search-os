#!/usr/bin/env python3
"""ready: write READY-FOR-YOU.md, the hand-off to the user. The engine stops here.

This step submits nothing and sends nothing. It lists, per channel, where to
submit and exactly which files, so the user can do it by hand.
"""
import datetime, json, os
from common import channels, finish, folder_arg, is_demo

folder = folder_arg()
st_p = os.path.join(folder, "run-state.json")
st = json.load(open(st_p, encoding="utf-8")) if os.path.exists(st_p) else {}
lines = []
if is_demo(folder):
    lines += ["DEMO — fictional candidate. Never use this for a real application.", ""]
lines += [f"# Ready for you to submit: {st.get('company', '?')} / {st.get('role', '?')}", "",
          f"Prepared {datetime.date.today().isoformat()}. Every engine check passed. "
          "Nothing has been submitted or sent: **you submit it.**", ""]
for key, ch in channels(folder).items():
    ch = ch or {}
    if ch.get("status") != "INTENDED":
        lines.append(f"- **{key}**: {ch.get('status')} ({ch.get('evidence', '')})")
        continue
    c = ch.get("contains") or {}
    lines += ["", f"## {key}", "", f"Submit at: {ch.get('submit_at')}", ""]
    lines += [f"- answer: `{a}`" for a in c.get("answers") or []]
    if c.get("resume"):
        lines.append(f"- resume: `{c['resume']}`")
    lines += [f"- attachment: `{a}`" for a in c.get("attachments") or []]
    for p in c.get("posting_artifacts") or []:
        label = p if isinstance(p, str) else " ".join(str(p.get(k)) for k in ("artifact", "question_id") if p.get(k))
        lines.append(f"- posting asked for: {label}")
lines += ["", "Paste each answer exactly as written, then reread what the site saved before you press submit."]
with open(os.path.join(folder, "READY-FOR-YOU.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
finish([], "READY-FOR-YOU.md written. The engine stops here; the user submits.")
