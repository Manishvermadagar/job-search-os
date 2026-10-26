#!/usr/bin/env python3
"""required_artifacts: an explicit list of what the posting demands, even if empty."""
from common import folder_arg, finish, load_json

folder = folder_arg()
d = load_json(folder, "required-artifacts.json")
problems = []
if d is None:
    problems.append("required-artifacts.json is missing. An empty list is a valid answer; a missing file is not.")
else:
    if not isinstance(d.get("items"), list):
        problems.append("'items' must be a list (use [] when the posting asks for nothing extra)")
    if not str(d.get("read_by", "")).strip():
        problems.append("'read_by' must record who read the posting for this")
    for i, it in enumerate(d.get("items") or []):
        if isinstance(it, dict) and not str(it.get("artifact", "")).strip():
            problems.append(f"item {i} has no 'artifact' name")
finish(problems, f"posting requires {len((d or {}).get('items') or [])} extra artifact(s)")
