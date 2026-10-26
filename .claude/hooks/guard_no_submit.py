#!/usr/bin/env python3
"""PreToolUse guard: this system never submits an application.

Denies, unconditionally, a browser script whose click target is an application
submit control (judged by submit_click_match.py). Reading pages, filling fields
for the user to check, and clicking anything else stay allowed.

Limit: a browser tool that clicks by an opaque element id carries no text to
judge, so it is not covered here. The agents' hard rule still applies to it.

Exit 0 = allow. Exit 2 = deny (stderr is shown to the agent).
"""
import json, os, re, sys

SCRIPT_TOOL = re.compile(r"evaluate|javascript|execute_script|run_script", re.I)


def deny(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


try:
    d = json.load(sys.stdin)
except ValueError:
    d = None
if not isinstance(d, dict):
    deny("DENIED - the no-submit guard could not read the tool call. Failing closed.")

tool = str(d.get("tool_name", ""))
if not SCRIPT_TOOL.search(tool):
    sys.exit(0)

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from submit_click_match import is_submit_click
except Exception as e:  # fail closed: a guard that cannot run must not allow
    deny(f"DENIED - the submit-click matcher did not load ({e}). Failing closed.")

inp = d.get("tool_input") or {}
script = " ".join(str(inp.get(k) or "") for k in ("function", "script", "expression", "text", "js", "code"))
if is_submit_click(script):
    deny(f"DENIED - '{tool}' would click an application submit control.\n"
         "job-search-os prepares applications and stops. The user submits them: "
         "see READY-FOR-YOU.md in the application folder.")
sys.exit(0)
