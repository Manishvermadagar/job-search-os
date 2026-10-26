# job-search-os: instructions for Codex and other agents

This repo is built for Claude Code subagents (`.claude/agents/`), but every role is
a plain Markdown instruction file, so any coding agent can run it.

**How to run it without subagents:** perform the roles one at a time, in the order
`CLAUDE.md` gives, by reading `.claude/agents/<role>.md` and then the skill it
points to. Write each role's output file before starting the next role.

For an application, let the engine set that order: `python engine/apply.py next
<folder>` names the step and its role, and `apply.py complete <folder> <node>` runs
the check that decides whether it is done. See "The application engine" in
`CLAUDE.md`. The Claude Code hooks do not run under other agents, so the
never-submit and never-send rules rest on you alone there.

Keep the separations that make the system work:

- When acting as `question-interpreter`, do not read `resume-data/career-bank.md`.
- When acting as `application-verifier`, read only the final answer, the literal
  question, `jd-posting.txt`, `company-research.md`, and `resume-data/career-bank.md`.
  Do not read briefs or drafting notes. Start a fresh session for it if you can.
- Never act as both writer and reviewer of the same text in one pass.

Everything in `CLAUDE.md` under **Hard rules** applies here unchanged: no invented
facts, never submit or send, never guess compensation, notice period or work
authorization.
