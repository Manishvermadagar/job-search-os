#!/usr/bin/env python3
"""apply.py - the application engine.

The engine owns the sequence. The agent executes one instructed step at a time
and may not look ahead, skip, reorder, or decide a step is unnecessary. A step
is done when its check program passes, not when the agent says so.

A failed check stops the run. Refusal is the start of a loop, not the end:

    next -> work -> complete -> checks run
                        | fail
                        v
                     BLOCKED
                   why -> what the check saw
                   fix -> record diagnosis + action (before any retry)
                   complete -> checks run again

Three failures on one node refuse a fourth attempt until the mistake is logged
in resume-data/resume-qa-ledger.md, because a step that keeps failing is usually
a badly designed step, not one that needs more effort.

The last node is 'ready'. The engine never submits an application and never
sends an email: it prepares, checks, and stops.

    apply.py start  <folder> --company X --role Y
    apply.py next   <folder>
    apply.py complete <folder> <node> --evidence '...'
    apply.py why    <folder> [node]
    apply.py fix    <folder> <node> --diagnosis '...' --action '...'
    apply.py status <folder>
    apply.py trace  <folder>
    apply.py abort  <folder> --reason '...'
"""
import argparse, datetime, json, os, subprocess, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ENGINE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ENGINE)
GRAPH = os.path.join(ENGINE, "process-graph.json")
LEDGER = os.path.join(REPO, "resume-data", "resume-qa-ledger.md")
MAX_ATTEMPTS = 3


def now():
    return datetime.datetime.now().isoformat(timespec="seconds")


def nodes():
    with open(GRAPH, encoding="utf-8") as f:
        return json.load(f)["nodes"]


def node_by_id(nid):
    return next((n for n in nodes() if n["id"] == nid), None)


def state_path(folder):
    return os.path.join(folder, "run-state.json")


def die(msg, code=2):
    print(("REFUSED: " if code else "") + msg, file=sys.stderr)
    sys.exit(code)


def load_state(folder):
    p = state_path(folder)
    if not os.path.exists(p):
        die(f"no run started in {folder}\n  start one:  apply.py start '{folder}' --company X --role Y")
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_state(folder, st):
    with open(state_path(folder), "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2)


def trace(folder, event, **kw):
    line = {"t": now(), "event": event, **kw}
    with open(os.path.join(folder, "trace.log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "\n")


def current_node(st):
    if st.get("aborted"):
        return None
    for nid in st["order"]:
        if st["nodes"][nid]["state"] in ("pending", "blocked"):
            return nid
    return None


def check_cmds(node):
    return [os.path.join(ENGINE, c) for c in node["checks"]]


def run_checks(node, folder):
    """Run every check for a node. All must pass; output is collected for 'why'."""
    outs, ok = [], True
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    for script in check_cmds(node):
        p = subprocess.run([sys.executable, script, folder], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", env=env)
        out = (p.stdout + p.stderr).strip()
        outs.append(f"[{os.path.relpath(script, ENGINE)}]\n{out}" if out else f"[{os.path.relpath(script, ENGINE)}]")
        if p.returncode != 0:
            ok = False
            break  # later checks assume earlier ones held
    return ok, "\n".join(outs)


def show_checks(node):
    return "\n".join("  python " + os.path.relpath(c, REPO) + " <folder>" for c in check_cmds(node))


# ---------------------------------------------------------------- commands

def cmd_start(a):
    os.makedirs(a.folder, exist_ok=True)
    if os.path.exists(state_path(a.folder)):
        die("a run already exists here. Use 'status' or 'next'.")
    ns = nodes()
    st = {"folder": a.folder, "company": a.company, "role": a.role, "started": now(),
          "order": [n["id"] for n in ns],
          "nodes": {n["id"]: {"state": "pending", "attempts": 0, "evidence": "", "last_error": ""}
                    for n in ns}}
    save_state(a.folder, st)
    trace(a.folder, "start", company=a.company, role=a.role, nodes=len(ns))
    print(f"run started: {a.company} / {a.role}, {len(ns)} nodes")
    print(f"next step:   apply.py next '{a.folder}'")


def cmd_next(a):
    st = load_state(a.folder)
    if st.get("aborted"):
        print(f"ABORTED: {st['aborted']['reason']}")
        return
    nid = current_node(st)
    if nid is None:
        print("READY: every node passed. See READY-FOR-YOU.md. The user submits.")
        return
    n, s = node_by_id(nid), st["nodes"][nid]
    bar = "=" * 72
    print(bar)
    print(f"STEP {st['order'].index(nid) + 1} of {len(st['order'])}:  {nid}   (agent: {n.get('agent', '-')})")
    print(f"  {n['label']}")
    print(bar)
    if s["state"] == "blocked":
        print(f"\n!! BLOCKED - attempt {s['attempts']} failed. What the check saw:")
        for ln in (s["last_error"] or "(no output)").splitlines():
            print("     " + ln)
        print(f"\n   fix:  apply.py fix '{a.folder}' {nid} --diagnosis '...' --action '...'")
        if s["attempts"] >= MAX_ATTEMPTS:
            print(f"\n   *** {s['attempts']} failures. A further retry is refused until")
            print(f"       resume-data/resume-qa-ledger.md has an entry mentioning '{nid}'.")
    print("\nRULES FOR THIS STEP:")
    for r in n["rules"]:
        print("  - " + r)
    print("\nHOW IT WILL BE CHECKED:")
    print(show_checks(n))
    print(f"\nwhen done:  apply.py complete '{a.folder}' {nid} --evidence '...'")


def cmd_complete(a):
    st = load_state(a.folder)
    if st.get("aborted"):
        die("this run was aborted.")
    cur = current_node(st)
    if cur is None:
        die("the run is already complete.")
    if a.node != cur:
        if a.node not in st["order"]:
            die(f"'{a.node}' is not a node in this run.")
        die(f"out of order. The current node is '{cur}' (step {st['order'].index(cur) + 1}); "
            f"you tried '{a.node}' (step {st['order'].index(a.node) + 1}).\n"
            f"  The engine owns the sequence. Run:  apply.py next '{a.folder}'")
    s = st["nodes"][cur]
    if s["state"] == "blocked":
        # The diagnosis is recorded BEFORE the retry. Without this the agent can
        # hammer 'complete' without ever stating what was wrong.
        trace(a.folder, "retry_without_fix_refused", node=cur, attempts=s["attempts"])
        die(f"'{cur}' is BLOCKED and no fix has been recorded.\n"
            f"    apply.py why '{a.folder}'\n"
            f"    apply.py fix '{a.folder}' {cur} --diagnosis '...' --action '...'")
    if s["attempts"] >= MAX_ATTEMPTS:
        txt = open(LEDGER, encoding="utf-8").read() if os.path.exists(LEDGER) else ""
        if cur not in txt:
            trace(a.folder, "retry_refused", node=cur, attempts=s["attempts"])
            die(f"'{cur}' has failed {s['attempts']} times. A further retry is refused until "
                f"resume-data/resume-qa-ledger.md has an entry mentioning '{cur}': what went wrong "
                f"and the rule that prevents it.")
    ok, out = run_checks(node_by_id(cur), a.folder)
    s["attempts"] += 1
    if not ok:
        s["state"], s["last_error"] = "blocked", out or "(check produced no output)"
        save_state(a.folder, st)
        trace(a.folder, "check_failed", node=cur, attempt=s["attempts"], output=out)
        print(f"REFUSED: '{cur}' did not pass its check (attempt {s['attempts']}).\n", file=sys.stderr)
        for ln in (out or "(no output)").splitlines():
            print("  " + ln, file=sys.stderr)
        print(f"\nfix it, record why, then retry:\n  apply.py fix '{a.folder}' {cur} "
              f"--diagnosis '...' --action '...'", file=sys.stderr)
        sys.exit(1)
    s.update(state="done", evidence=a.evidence or "", last_error="")
    save_state(a.folder, st)
    trace(a.folder, "node_done", node=cur, attempt=s["attempts"], evidence=a.evidence or "")
    nxt = current_node(st)
    print(f"PASS: {cur}")
    print("\n".join("  " + ln for ln in out.splitlines()[:6]))
    print(f"next: {nxt if nxt else '- READY. The engine stops here; the user submits.'}")


def cmd_why(a):
    st = load_state(a.folder)
    nid = a.node or current_node(st)
    if nid is None:
        die("nothing in progress.")
    s, n = st["nodes"][nid], node_by_id(nid)
    print(f"{nid} - state={s['state']} attempts={s['attempts']}\n  {n['label']}\n")
    print("what the check saw last time:")
    for ln in (s["last_error"] or "(nothing - it has not failed)").splitlines():
        print("  " + ln)
    print("\nthe checks:\n" + show_checks(n))
    print("\nrules for this step:")
    for r in n["rules"]:
        print("  - " + r)


def cmd_fix(a):
    st = load_state(a.folder)
    if a.node not in st["nodes"]:
        die(f"'{a.node}' is not a node in this run.")
    s = st["nodes"][a.node]
    if s["state"] != "blocked":
        die(f"'{a.node}' is not blocked (state={s['state']}). fix is for blocked nodes.")
    trace(a.folder, "fix", node=a.node, attempt=s["attempts"], diagnosis=a.diagnosis, action=a.action)
    s["state"] = "pending"
    save_state(a.folder, st)
    print("recorded. The diagnosis and action are in trace.log before the retry, so every")
    print("repair can be inspected afterwards; repairs are where fresh defects come from.")
    print(f"\nretry:  apply.py complete '{a.folder}' {a.node} --evidence '...'")


def cmd_status(a):
    st = load_state(a.folder)
    print(f"{st['company']} / {st['role']}  started {st['started']}")
    if st.get("aborted"):
        print(f"  ABORTED: {st['aborted']['reason']}")
    for i, nid in enumerate(st["order"], 1):
        s = st["nodes"][nid]
        mark = {"done": "[x]", "pending": "[ ]", "blocked": "[!]"}[s["state"]]
        extra = f"  attempts={s['attempts']}" if s["attempts"] else ""
        ev = f"  {s['evidence'][:60]}" if s["evidence"] else ""
        print(f"  {mark} {i:2}. {nid}{extra}{ev}")


def cmd_trace(a):
    p = os.path.join(a.folder, "trace.log")
    if not os.path.exists(p):
        die("no trace yet.")
    for line in open(p, encoding="utf-8"):
        d = json.loads(line)
        t, e = d.pop("t"), d.pop("event")
        print(f"{t}  {e:16} " + "  ".join(f"{k}={str(v)[:70]}" for k, v in d.items()))


def cmd_abort(a):
    """End a run that cannot or should not proceed. An aborted run is a normal
    outcome, not a failure; without an ending, half-finished work looks like progress."""
    st = load_state(a.folder)
    if st.get("aborted"):
        die(f"already aborted: {st['aborted']['reason']}")
    done = [n for n in st["order"] if st["nodes"][n]["state"] == "done"]
    st["aborted"] = {"at": now(), "reason": a.reason, "reached": done[-1] if done else None}
    save_state(a.folder, st)
    trace(a.folder, "abort", reason=a.reason, nodes_done=len(done))
    print(f"ABORTED: {st['company']} / {st['role']}")
    print(f"  reason:  {a.reason}")
    print(f"  reached: {done[-1] if done else 'nothing'} ({len(done)}/{len(st['order'])} nodes)")
    print("  Record the skip and its reason in resume-data/job-search/.")


def main():
    ap = argparse.ArgumentParser(prog="apply.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start"); s.add_argument("folder")
    s.add_argument("--company", required=True); s.add_argument("--role", required=True)
    s.set_defaults(fn=cmd_start)
    s = sub.add_parser("next"); s.add_argument("folder"); s.set_defaults(fn=cmd_next)
    s = sub.add_parser("complete"); s.add_argument("folder"); s.add_argument("node")
    s.add_argument("--evidence", default=""); s.set_defaults(fn=cmd_complete)
    s = sub.add_parser("why"); s.add_argument("folder"); s.add_argument("node", nargs="?")
    s.set_defaults(fn=cmd_why)
    s = sub.add_parser("fix"); s.add_argument("folder"); s.add_argument("node")
    s.add_argument("--diagnosis", required=True); s.add_argument("--action", required=True)
    s.set_defaults(fn=cmd_fix)
    s = sub.add_parser("status"); s.add_argument("folder"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("trace"); s.add_argument("folder"); s.set_defaults(fn=cmd_trace)
    s = sub.add_parser("abort"); s.add_argument("folder"); s.add_argument("--reason", required=True)
    s.set_defaults(fn=cmd_abort)
    a = ap.parse_args()
    a.folder = os.path.abspath(a.folder)
    a.fn(a)


if __name__ == "__main__":
    main()
