---
name: job-application-pipeline
description: Use when the user wants to work one or more job postings end to end — find roles, check eligibility and liveness, analyse the JD, tailor a resume, write each application answer through the writing team, optionally get an external review, and prepare the complete application on every channel that applies (job board, company careers page, careers email). Site-agnostic. Prepares and presents only; it never submits an application or sends an email — the user does that.
---

# Job Application Pipeline

This skill is the method behind the "Find jobs" and "Apply to one posting"
pipelines in the repo's `CLAUDE.md`. The orchestrator hands each step to an agent
in `.claude/agents/`; this file says what each step must produce and what must be
true before moving on.

**The system prepares; the user submits.** Nothing in this pipeline submits a
form, clicks a final Apply/Submit/Send, or sends an email. A reviewer's verdict,
a standing preference or a "READY" status never authorizes transmitting. The last
step is always: show the user the complete application and stop.

## Before starting

Read, in this order:

1. `resume-data/career-bank.md` — the only source of facts. If it is missing or
   still the example, run Setup from `CLAUDE.md` first.
2. `resume-data/standing-preferences.md` — locations, remote/onsite, work
   authorization, notice period, and other answers given once.
3. `resume-data/salary-thresholds.md` — break-even, real-hike and walk-away pay.
4. `resume-data/resume-qa-ledger.md` — past mistakes and the rules that prevent
   them.
5. The relevant `resume-data/profiles/<slug>.md`.

State which files were read. A skipped preflight should be visible.

## Phase 0 — Find roles (`job-selector`)

Run the `job-selector` agent/skill over the board or feed. It writes
`resume-data/job-search/SHORTLIST.md` with a fit rating and reasons, and records
skipped roles with the reason. Show the shortlist to the user and let them choose
what to pursue. Do not start an application the user has not chosen.

## Phase 1 — Eligibility and liveness, before any effort

Work through `references/eligibility-checklist.md` on the **full posting text**,
never on a search-results card. Then confirm the posting is worth effort:

- **Liveness.** A dead listing can still load with its full JD. Look for the
  board's explicit "no longer available" text, check the posting date and any
  "last active" signal, and check whether the employer's own careers page lists
  the role. If the board says open and the careers page says no open roles, flag
  it to the user before drafting anything.
- **Employer is real.** Check the website the employer itself listed (not a
  similar-looking domain): it should load real content, not a parking page, and
  should not be newly registered relative to the posting. Weigh this most when
  the role handles other people's personal data.
- **Hard requirements.** List every "must have" in the JD and mark each as
  met (with the `career-bank.md` line), partly met, or not met. Report an unmet
  factual bar, such as work authorization, a required license, or technical
  depth the career bank rules out. For a stated year count, compare the work
  and scope described in the posting with the candidate's verified experience;
  follow `job-selector`'s rule that the number alone is not a rejection.
- **Compensation.** Compare the posted band, converted to the user's currency and
  period, against `salary-thresholds.md`. Below walk-away is a skip unless the
  user says otherwise.

Output: an eligibility note in the application folder (see below) with a
recommendation — pursue, pursue with flagged risk, or skip — and why.

## Phase 1.5 — Channel discovery, before tailoring

Find out how the role can actually be applied to before preparing content.
Tailoring a resume for a channel that never transmits one is wasted work.

1. **Walk the apply flow without submitting.** Open the form and advance through
   every step, stopping before any final submit control. Record every question
   with its exact wording, word limits, required yes/no gates, file uploads, and
   any blocker: a location restriction shown only inside the flow, "not accepting
   applications", a required assessment, forced account creation, or a redirect to
   another applicant-tracking system. Question sets are per posting — never assume
   one posting's questions from another, even at the same company.
2. **Confirm every apply link opens the intended live posting**, with the right
   title. Careers pages sometimes point at stale tracking-system ids.
3. **Read the posting's own instructions.** If it says "apply only through this
   portal" or "no direct contact", respect that and do not add channels.
4. **Company careers page.** Check whether the same role is listed. Treat it as the
   same role only when employer, title and substantive requirements clearly
   match; otherwise it is a separate opportunity the user decides on. Record the
   result precisely: `listed`, `confirmed absent`, `not accessible`, or
   `not found after search` — these mean different things later.
5. **Careers email.** Look for a published `careers@` / `jobs@` / `hr@` address or a
   recruiter address given in the posting. Never use a scraped personal address
   and never guess addresses. If the company is very small, ask the user whether
   a second contact on top of the board application is wise.
6. **Decide:** if no channel accepts a document (profile-based boards), skip
   resume tailoring and say so in the folder README; otherwise tailor in Phase 2.

Note: the board's own structured fields (e.g. "hires remotely everywhere") can
contradict the employer's posting or form. The employer's own words win; record
the conflict in `jd-posting.txt`.

## Application folder convention

One folder per **application instance** (one submission to one destination):
`resume-data/output/<role>-<company>-<channel>/`, e.g.
`ops-manager-acme-board`, `ops-manager-acme-careers`, `ops-manager-acme-email`.
Two channels for the same role never share a folder. Each folder holds:

| File | Contents |
|---|---|
| `README.md` | Status, channels checked and their results, decisions not to relitigate |
| `jd-posting.txt` | Verbatim posting plus listing metadata not in the JD body (pay, location field, apply mechanics, form questions) |
| `jd-analysis.md` | From `jd-analyst`: requirements, keywords, pillar mapping, open risks |
| `eligibility.md` | Phase 1 output |
| `resume.md` + renders | Tailored resume; renders named `<Role>_<Name>.pdf/.docx` |
| `application-answers.md` | Every form question, its resolution bucket, and the final text |
| `cover-email.md` | Draft only, if an email channel exists |
| `reviews/` | Verifier and external-review records, each naming the file it reviewed |

The folder should let anyone resume the application without the conversation.

## Phase 2 — Analyse the JD and tailor the resume

1. `jd-analyst` writes `jd-posting.txt` and `jd-analysis.md`.
2. `resume-builder` tailors from the **closest existing resume** in
   `resume-data/output/` when the role, seniority and profile are genuinely
   similar; build fresh only when adapting would fight the new JD.
3. `resume-reviewer` loops until `VERDICT: READY`. Every claim must trace to
   `career-bank.md`.
4. Render PDF and DOCX, then verify by extracting the text — a clean exit is not
   proof the render is right.

## Phase 3 — Resolve the form, then write only what is missing

Sort every field from the walked form into one bucket:

| Bucket | What it is | What happens |
|---|---|---|
| **FACT** | Asked literally and stable: name, email, phone, degree, years of experience, which file to upload, a yes/no eligibility gate already answered in `standing-preferences.md` | Filled from `standing-preferences.md` / `career-bank.md`. No writing needed |
| **WRITE** | Assesses the candidate: why us, describe, explain, tell us about | Goes through the writing team (Phase 4), written for this job |
| **ASK** | Compensation, notice period, work authorization, relocation, start date, date of birth, any government ID or payment detail — when not already in `standing-preferences.md` | Stop and ask the user. Never infer |
| **BLOCKED** | CAPTCHA, account creation with a password, required assessment, unrecognised required field | Report to the user; the system does not proceed |

There is no answer bank. Assessment answers are written per posting; identical
text across employers reads as canned and cannot be calibrated to the JD.

## Phase 4 — The writing team, per question

For each WRITE field, cover letter or cover email, run in order:

1. `question-interpreter` — what was literally asked and what decision the reader
   is making. Blind to the candidate's achievements.
2. `application-strategist` — researches the company, generates 3–5 competing
   angles, picks one, and lists exclusions.
3. `application-writer` — turns the chosen angle into prose for that genre and
   length, following `references/application-writing-style.md`.
4. `application-verifier` — pass/fail on truth, question fit, company anchoring,
   relevance and memorability, without seeing the writer's reasoning. On FAIL,
   route the repair by failure class using the verifier skill's routing table.
   After revision, run the writer and verifier again on the complete final text.

Independent questions can run in parallel. Watch for **scope migration**: a true
fact restated at a wider scope than the career bank grants (one team's result
becoming the whole department's).

## Phase 5 — Optional external review

If the user wants a second opinion, `external-reviewer` (see the
`ai-cross-reviewer` skill) reviews the final texts. Rules:

- Attach the real files, never a summary of them. Do not narrate your own edits.
- Ask one question per round; check correctness before style.
- Every suggestion is checked against `career-bank.md` before use. A reviewer
  asking to restore a claim the career bank rules out is not evidence for it.
- A reviewer's approval means the text is ready to show the user. It never
  authorizes submission.

## Phase 6 — Present to the user and stop

Show, per channel: the apply URL, every field with its final value, the files to
upload, any ASK items still open, and any flagged risks. If the user asks for help
filling a form, fill fields and stop before the final submit control; verify each
field by reading its value back. Email is prepared as a draft only.

Only the user submits. When they confirm a channel went out, record it.

## Tracking

Update the tracker in `resume-data/job-search/` for every row touched:

- `applying` — being built
- `ready-for-user` — complete and shown, waiting on the user
- `applied` — the user confirmed submission (note which channel)
- `uncertain` — the user tried and saw no clear confirmation
- `skip` — not pursued, with the reason

Never mark `applied` on the system's own say-so. A sent application is
immutable: keep its final text as `*-AS-SENT.*` and do not edit it afterwards.

## Guardrails

- Never submit an application, click a final submit control, or send an email.
- Never guess compensation, notice period, work authorization, date of birth or
  IDs. Use `standing-preferences.md` or ask.
- Never invent a fact. If one is missing, ask the user and add it to
  `career-bank.md` first.
- One application at a time, finished on every applicable channel before the
  next starts. Half-finished applications look like progress and are not.
- Verify by value: reload and re-read a saved field, extract text from a render,
  rely on the site's own confirmation.
- When an agent's output was wrong, log the mistake and the preventing rule in
  `resume-data/resume-qa-ledger.md`.
