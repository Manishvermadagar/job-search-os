#!/usr/bin/env python3
"""Self-test for the application engine and the safety hooks.

Runs the finished demo application in tests/fixtures/demo-northwind through every
engine node, then breaks it in the ways real applications break and checks each
one is refused. Stdlib only; writes only to a temporary directory.

    python tests/selftest.py
"""
import json, os, shutil, subprocess, sys, tempfile, time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(REPO, "tests", "fixtures", "demo-northwind")
APPLY = os.path.join(REPO, "engine", "apply.py")
CHECKS = os.path.join(REPO, "engine", "checks")
HOOKS = os.path.join(REPO, ".claude", "hooks")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8")
ENV.pop("JSO_CAREER_BANK", None)

passed, failed = 0, []


def step(name, ok, detail=""):
    global passed
    if ok:
        passed += 1
        print("  PASS  " + name)
    else:
        failed.append(name)
        print("  FAIL  " + name + (f"\n        {detail[:400]}" if detail else ""))


def run(args, stdin=None):
    p = subprocess.run([sys.executable] + args, input=stdin, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=ENV)
    return p.returncode, p.stdout + p.stderr


def fresh(parent=None, name="demo-selftest"):
    """A copy of the fixture with every file's mtime equalised, so checks that
    compare modification times see a consistent order on any checkout."""
    parent = parent or tempfile.mkdtemp(prefix="jso-")
    dst = os.path.join(parent, name)
    shutil.copytree(FIXTURE, dst)
    t = time.time() - 100
    for root, _, files in os.walk(dst):
        for f in files:
            os.utime(os.path.join(root, f), (t, t))
    return dst


def check(name, folder):
    return run([os.path.join(CHECKS, name), folder])


def edit_json(path, fn):
    d = json.load(open(path, encoding="utf-8"))
    fn(d)
    json.dump(d, open(path, "w", encoding="utf-8"), indent=2)


def touch_later(path, secs=50):
    t = time.time() - 100 + secs
    os.utime(path, (t, t))


ORDER = [n["id"] for n in json.load(open(os.path.join(REPO, "engine", "process-graph.json"),
                                         encoding="utf-8"))["nodes"]]

# ------------------------------------------------------------------ engine
print("\n=== engine: the demo application runs to 'ready' ===")
f = fresh()
rc, out = run([APPLY, "start", f, "--company", "Northwind (fictional)", "--role", "Operations Manager"])
step("start a run", rc == 0, out)
rc, out = run([APPLY, "complete", f, "channels"])
step("completing a node out of order is refused", rc == 2 and "out of order" in out, out)
ok = True
for nid in ORDER:
    rc, out = run([APPLY, "complete", f, nid, "--evidence", "selftest"])
    if rc != 0:
        ok = False
        step(f"node '{nid}' passes on the finished demo", False, out)
        break
step(f"all {len(ORDER)} nodes pass in order on the finished demo", ok)
step("'ready' writes READY-FOR-YOU.md, and it says the user submits",
     ok and "you submit it" in open(os.path.join(f, "READY-FOR-YOU.md"), encoding="utf-8").read())
rc, out = run([APPLY, "next", f])
step("after 'ready' the engine reports READY and offers nothing further", "READY" in out, out)

print("\n=== engine: refusal loop ===")
f = fresh()
run([APPLY, "start", f, "--company", "X", "--role", "Y"])
os.remove(os.path.join(f, "jd-analysis.md"))
rc, out = run([APPLY, "complete", f, "jd_capture"])
step("a failing check blocks the node", rc == 1 and "jd-analysis.md" in out, out)
rc, out = run([APPLY, "complete", f, "jd_capture"])
step("retrying a blocked node without a recorded fix is refused", rc == 2 and "no fix has been recorded" in out, out)
for _ in range(2):
    run([APPLY, "fix", f, "jd_capture", "--diagnosis", "d", "--action", "a"])
    run([APPLY, "complete", f, "jd_capture"])
run([APPLY, "fix", f, "jd_capture", "--diagnosis", "d", "--action", "a"])
rc, out = run([APPLY, "complete", f, "jd_capture"])
step("a fourth attempt after three failures is refused until the QA ledger names the node",
     rc == 2 and "resume-qa-ledger.md" in out, out)
rc, out = run([APPLY, "abort", f, "--reason", "selftest"])
rc2, out2 = run([APPLY, "complete", f, "jd_capture"])
step("an aborted run accepts no further steps", rc == 0 and rc2 == 2, out + out2)

# ------------------------------------------------------------------ checks
print("\n=== checks: the ways real applications break ===")
f = fresh()
with open(os.path.join(f, "answers", "q2.md"), "a", encoding="utf-8") as fh:
    fh.write("\nIn my experience, support teams always fix routing last.\n")
rc, out = check("grounding.py", f)
step("an unsourced generalisation ('in my experience ... always') is UNSUPPORTED and blocks", rc == 1 and "LAUNDERING" in out, out)
with open(os.path.join(f, "answers", "q2.md"), "a", encoding="utf-8") as fh:
    fh.write("\nI cut handling time by 37 percent.\n")
rc, out = check("grounding.py", f)
step("a figure that appears in no source blocks", rc == 1 and "37" in out, out)
g = os.path.join(f, "grounding", "q2.json")
edit_json(g, lambda d: [s.update(disposition="RHETORICAL") for s in d["sentences"] if s["status"] == "UNSUPPORTED"])
rc, out = check("grounding.py", f)
step("recorded dispositions survive the re-run and clear the node", rc == 0, out)

f = fresh()
touch_later(os.path.join(f, "answers", "q1.md"))
rc, out = check("verifications.py", f)
step("an answer edited after its verification is refused", rc == 1 and "changed after" in out, out)
f = fresh()
with open(os.path.join(f, "verification.md"), "a", encoding="utf-8") as fh:
    fh.write("\n## answers/q2.md\n\nVERDICT: FAIL\n")
rc, out = check("verifications.py", f)
step("the LATEST verdict for a file counts, not an earlier PASS", rc == 1 and "FAIL" in out, out)

f = fresh()
touch_later(os.path.join(f, "resume.md"))
rc, out = check("resume.py", f)
step("a resume edited after review and render is refused", rc == 1 and ("changed after review" in out or "STALE" in out), out)

f = fresh()
edit_json(os.path.join(f, "channels.json"), lambda d: d.update(email={
    "status": "INTENDED", "evidence": "published address", "submit_at": "jobs@example.invalid",
    "contains": {"answers": ["answers/q1.md"], "attachments": []}}))
rc, out = check("composition.py", f)
step("an email channel with no resume attached fails composition", rc == 1 and "NO RESUME ATTACHED" in out, out)
f = fresh()
edit_json(os.path.join(f, "channels.json"), lambda d: d["job_board"]["contains"].update(posting_artifacts=[]))
rc, out = check("composition.py", f)
step("a channel missing an artifact the posting requires fails composition", rc == 1 and "q1" in out, out)
f = fresh()
open(os.path.join(f, "banned-evidence.txt"), "w").write("[all]\n4,000\\+ tickets\n")
rc, out = check("banned_evidence.py", f)
step("evidence banned for this application is caught in answers AND the rendered resume",
     rc == 1 and ":answer" in out and ":resume" in out, out)

f = fresh()
os.remove(os.path.join(f, "external-review-skipped.md"))
rc, out = check("external_review.py", f)
step("no external review and no recorded skip reason fails", rc == 1, out)
f = fresh()
os.makedirs(os.path.join(f, "review"))
open(os.path.join(f, "review", "review-round-1.md"), "w").write(
    "answers/q1.md answers/q2.md\nDEMO Operations Manager_Avery Example.pdf\nVERDICT: READY TO SUBMIT\n")
touch_later(os.path.join(f, "review", "review-round-1.md"), 10)
touch_later(os.path.join(f, "answers", "q2.md"), 40)
rc, out = check("external_review.py", f)
step("an external review older than the answer it covers is refused", rc == 1 and "changed after" in out, out)

f = fresh()
edit_json(os.path.join(f, "channels.json"), lambda d: d["careers_page"].update(evidence=""))
rc, out = check("channels.py", f)
step("a channel with no record of what was checked fails", rc == 1 and "careers_page" in out, out)
f = fresh()
txt = open(os.path.join(f, "eligibility.md"), encoding="utf-8").read().replace("VERDICT: PROCEED", "VERDICT: SKIP")
open(os.path.join(f, "eligibility.md"), "w", encoding="utf-8").write(txt)
rc, out = check("eligibility.py", f)
step("VERDICT: SKIP does not pass; it points to abort", rc == 1 and "abort" in out, out)

parent = tempfile.mkdtemp(prefix="jso-")
done = fresh(parent, "demo-earlier")
run([APPLY, "start", done, "--company", "A", "--role", "B"])
for nid in ORDER:
    run([APPLY, "complete", done, nid])
again = fresh(parent, "demo-later")
rc, out = check("repetition.py", again)
step("an answer reused from a finished application is flagged", rc == 1 and "demo-earlier" in out, out)

# ------------------------------------------------------------------ hooks
print("\n=== hooks: never send, never submit ===")
rc, out = run([os.path.join(HOOKS, "submit_click_match.py"), "--selftest"])
step("submit-click matcher selftest (13 cases)", rc == 0 and "13/13" in out, out)


def hook(name, payload):
    return run([os.path.join(HOOKS, name)], json.dumps(payload))


for tool in ("mcp__gmail__send_email", "mcp__gmail-personal__send_draft", "mcp__mail__reply_all"):
    rc, out = hook("guard_no_send.py", {"tool_name": tool, "tool_input": {}})
    step(f"no-send guard denies {tool}", rc == 2, out)
rc, out = hook("guard_no_send.py", {"tool_name": "mcp__gmail__draft_email", "tool_input": {}})
step("no-send guard allows drafting", rc == 0, out)
for name in ("guard_no_send.py", "guard_no_submit.py"):
    bad = [run([os.path.join(HOOKS, name)], raw)[0] for raw in ("not json", '"a string"', "[]")]
    step(f"{name} fails closed on an unreadable or non-object call", bad == [2, 2, 2], str(bad))
rc, out = hook("guard_no_submit.py", {"tool_name": "mcp__chrome-devtools__evaluate_script",
                                      "tool_input": {"function": '() => document.querySelector("#submit-application").click()'}})
step("no-submit guard denies a click on an application submit control", rc == 2, out)
rc, out = hook("guard_no_submit.py", {"tool_name": "mcp__chrome-devtools__evaluate_script",
                                      "tool_input": {"function": "() => document.body.innerText"}})
step("no-submit guard allows reading a page", rc == 0, out)
settings = json.load(open(os.path.join(REPO, ".claude", "settings.json"), encoding="utf-8"))
cmds = [h["command"] for e in settings["hooks"]["PreToolUse"] for h in e["hooks"]]
step("both guards are registered with $CLAUDE_PROJECT_DIR paths",
     all("$CLAUDE_PROJECT_DIR" in c for c in cmds) and any("guard_no_send" in c for c in cmds)
     and any("guard_no_submit" in c for c in cmds), str(cmds))

print(f"\n{passed} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
