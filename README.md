# job-search-os

A multi-agent job-search system for [Claude Code](https://claude.com/claude-code).
It builds resumes from a single source of facts, shortlists jobs by reasoning
about fit rather than keywords, and prepares each application through a small
team of agents that check one another's work.

It never submits an application or sends an email for you. It prepares, shows
you, and stops.

## How it works

Everything starts from one file: `resume-data/career-bank.md`, every real fact
about your work history. Agents may reorder and reframe those facts. They may not
invent any.

| Agent | Job |
|---|---|
| `job-selector` | Reads job listings and shortlists the ones you could do, with the quote that decided each |
| `jd-analyst` | Breaks one posting into requirements and maps each to your evidence |
| `resume-builder` | Positions, drafts, de-AIs and renders your resume to PDF and DOCX |
| `resume-reviewer` | Critiques the draft against an ATS and fact checklist; pass or fail |
| `question-interpreter` | Works out what an application question actually asks (never sees your achievements) |
| `application-strategist` | Researches the company and picks the strongest angle |
| `application-writer` | Writes the answer, cover letter or email |
| `application-verifier` | Final pass/fail gate on truth and fit (never sees the writer's notes) |
| `external-reviewer` | Optional second opinion from another model through the Codex CLI |

The orchestrator in `CLAUDE.md` chains them. Each agent is a short file in
`.claude/agents/` that points to a detailed method in `.claude/skills/`.

```
Find jobs:     job-selector ─▶ SHORTLIST.md ─▶ you choose
Apply:         jd-analyst ─▶ resume-builder ─▶ resume-reviewer
               └─ per question: interpreter ─▶ strategist ─▶ writer ─▶ verifier
               ─▶ (external-reviewer) ─▶ you review and submit
```

## Requirements

- [Claude Code](https://claude.com/claude-code)
- Python 3.10+ with `reportlab` and `python-docx`
  (`pip install reportlab python-docx`)
- `pdftotext` (poppler) to verify rendered PDFs
- Optional: the [Codex CLI](https://github.com/openai/codex), signed in, for
  external review

## Quick start

```bash
git clone https://github.com/Manishvermadagar/job-search-os.git
cd job-search-os
claude
```

Then tell Claude: **"Set me up."** It copies the templates into `resume-data/`,
reads your existing resume if you have one, and fills your career bank with you.

Try it without your own data first: **"Run the demo: apply to
examples/sample-posting.txt using examples/sample-career-bank.md."** This runs in
demo mode on a fictional candidate; outputs are labelled DEMO and land in
`resume-data/output/demo-*/`.

After setup, ask for what you want:

- "Build me a resume for operations manager roles."
- "Scan this job board and shortlist what fits: <url>"
- "Prepare my application for this posting: <url>"

## Using it with Codex or another agent

`AGENTS.md` explains how to run the same roles one at a time without subagents.

## Your data

`resume-data/` is git-ignored apart from its empty folders. Your career bank,
resumes and applications stay on your machine.

## Ground rules the agents follow

- No invented facts. Every claim traces to your career bank.
- No submissions or sent emails. You do that.
- No guessed compensation, notice period or work authorization.
- Verify by value: reread what was saved, extract the text of what was rendered.

## Author

Built and maintained by **Manish Verma** ([GitHub](https://github.com/Manishvermadagar) ·
[LinkedIn](https://www.linkedin.com/in/vermamanish111)).

Issues and pull requests are welcome. If you use or adapt this system, a link
back is appreciated.

## Licence

[MIT](LICENSE) © 2026 Manish Verma. You may use, modify and share it; keep the
copyright notice.

## Credits

The `humanizer` skill is adapted from [blader/humanizer](https://github.com/blader/humanizer)
(MIT, © 2025 Siqi Chen), which is based on Wikipedia's
[Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
guide. See [NOTICE.md](NOTICE.md).
