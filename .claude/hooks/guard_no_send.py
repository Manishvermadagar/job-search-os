#!/usr/bin/env python3
"""PreToolUse guard: this system never sends email.

Denies, unconditionally, any MCP tool that sends, replies to or forwards mail,
whatever mail server provides it. Drafting stays allowed: the user reviews the
draft and sends it themselves.

Exit 0 = allow. Exit 2 = deny (stderr is shown to the agent).
"""
import json, re, sys

SEND = re.compile(r"(^|__)(send_email|send_draft|send_mail|send_message_email|reply_all|reply_email|"
                  r"reply_to_email|forward_email|forward_message)$", re.I)

try:
    d = json.load(sys.stdin)
except ValueError:
    d = None
if not isinstance(d, dict):
    print("DENIED - the no-send guard could not read the tool call. Failing closed.", file=sys.stderr)
    sys.exit(2)

tool = str(d.get("tool_name", ""))
if SEND.search(tool):
    print(f"DENIED - '{tool}'. job-search-os never sends email on your behalf.\n"
          "Write the message as a draft instead (draft_email), show it to the user, "
          "and let them send it.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
