#!/usr/bin/env bash
# Runs a Python hook with whichever interpreter works on this machine.
# On Windows, "python3" can be a Microsoft Store stub that exits non-zero, so
# each candidate is tried. If none works the hook FAILS CLOSED (exit 2): a guard
# that cannot run must not silently allow.
HOOK="${0%/*}/$1"
for py in python3 python py; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c "" >/dev/null 2>&1; then
    exec "$py" "$HOOK"
  fi
done
echo "DENIED - no working Python found to run $1. Failing closed." >&2
exit 2
