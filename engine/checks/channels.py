#!/usr/bin/env python3
"""channels: every channel checked is decided and evidenced; blank fails."""
from common import CHANNEL_STATES, channels, folder_arg, finish

folder = folder_arg()
d = channels(folder)
problems = []
if not d:
    problems.append("channels.json is empty - record every channel you checked")
for key, ch in d.items():
    ch = ch or {}
    if ch.get("status") not in CHANNEL_STATES:
        problems.append(f"{key}: status must be one of {', '.join(CHANNEL_STATES)}")
    if not str(ch.get("evidence", "")).strip():
        problems.append(f"{key}: 'evidence' must say what was checked")
    if ch.get("status") == "INTENDED":
        c = ch.get("contains") or {}
        if not c.get("answers"):
            problems.append(f"{key}: INTENDED but 'contains.answers' lists nothing to send")
        if not str(ch.get("submit_at", "")).strip():
            problems.append(f"{key}: INTENDED needs 'submit_at' - the URL or published address the user will use")
if d and not any((c or {}).get("status") == "INTENDED" for c in d.values()):
    problems.append("no channel is INTENDED. If none is usable, abort the run instead.")
finish(problems, f"channels decided: " + ", ".join(f"{k}={(v or {}).get('status')}" for k, v in d.items()))
