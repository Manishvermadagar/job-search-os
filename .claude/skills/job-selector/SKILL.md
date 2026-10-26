---
name: job-selector
description: Use whenever scanning a job board for roles to apply to — LinkedIn, Indeed, Wellfound, a company careers page, any listing feed. Three passes over the raw text of every listing, selecting by reasoning against career-bank.md rather than by keyword matching. Produces a shortlist for the user to choose from; never applies to anything.
---

# Job Selector

## The rule that defines this skill

> **Never write code that decides which roles qualify.**

Code is fine — necessary, even — for **collecting** listing text off a page. It
is never used to **judge** a listing. A regex cannot read "Head of Operations",
know what the candidate actually did, and reason about whether they could do the
job. It can only match strings someone thought of in advance, and the strings
nobody thought of are where many opportunities are.

Keyword filters fail in both directions: they miss whole title families
(*solutions partner*, *general manager*, *chief of staff*) and their exclusion
lists cut good roles whose titles happen to contain a blocked word.

**Code collects. Judgment selects.**

## The question for every listing

Not *"is this the candidate's job title?"* but:

> **Could the candidate do this job well enough to be hired, and does it meet
> their goals (pay, arrangement, direction) better than their current role?**

The second question is much wider than the first. If the user has stated their
own goal in `standing-preferences.md`, reflect it here.

## What the candidate can actually do — reason from this, not from a title list

Before Pass 1, build a capability list from `career-bank.md`: one line per real
capability, each with the evidence behind it (scope, volume, outcome). Typical
headings:

- Run an operation or function
- Hire, train and manage performance
- Design process where none exists
- Handle the hardest customer or stakeholder situations
- Build or direct tooling
- Audit and establish what is actually true
- Analyse and report

**Hard ceilings — these do not move:** list what `career-bank.md` says the
candidate has never done (tools with zero exposure, responsibilities never
owned, technical-depth limits). The selector rejects on these and nothing softer.

---

# THE THREE PASSES

## PASS 1 — TITLE SCAN (every listing, no exceptions)

**Input:** every listing's title. Use code to collect it (scroll, accumulate,
handle feeds that unmount rows), then **read the list.**

For each title ask:

> **Is there any version of this job the candidate could do?**

**Default is KEEP.** A title drops here only when it is unambiguously not the
candidate: another profession entirely (nurse, attorney, biologist), a build role
the career bank does not support (engineer, developer, designer, data scientist),
pure creative production, or a structure that is not a job (unpaid, volunteer,
commission-only, equity-only).

**Everything else survives Pass 1, including:**
- Titles the candidate has never held, including more senior ones — seniority is
  a Pass 3 question.
- Titles in unfamiliar domains. Domain is often learnable and often only
  "preferred".
- Vague titles (*Associate, Generalist, Specialist, Partner, Coordinator,
  Analyst*). These hide both the best and worst listings.
- Hybrid titles where one half matches the candidate.

**When unsure, keep it.** A title costs seconds to carry into Pass 2; a missed
role costs an opportunity.

## PASS 2 — CARD SCAN (survivors of Pass 1)

Read the rest of the listing card: compensation, location, remote policy, hiring
region, posted date, company size and stage. Judge against:

- **Compensation** against `resume-data/salary-thresholds.md`, per arrangement
  (remote, relocation). Convert currencies at a **looked-up** rate, never a
  remembered one, and check whether a figure is annual or monthly.
- **Country and work authorization** against `standing-preferences.md`. A
  country restriction or visa requirement the candidate cannot meet is a bar.
- **Timezone and working hours** — a bar only if `standing-preferences.md` says
  so.
- **Posted date** — a filter only when the queue is too long to work.

Output: a shortlist with comp, region, link and a one-line note. **No fit verdict
yet** — fit is Pass 3.

## PASS 3 — JD SCAN (one listing at a time)

Open the posting and read the whole description. Only now decide.

**Reject only on a factual bar** (see also
`.claude/skills/job-application-pipeline/references/eligibility-checklist.md`):
1. A country or legal work-authorization requirement the candidate cannot meet.
2. A capability `career-bank.md` says the candidate lacks, stated as a
   **requirement** (not "preferred") — for example a language, a level of
   technical skill, or a named tool at zero exposure.
3. Compensation below the walk-away threshold once the real figure is known.

### Years of experience is not a bar

A stated year count ("5+ years", "8-12 years") is a proxy the employer wrote for
scope they could not describe. Compare the candidate's real scope instead — team
size and functions run, people hired and managed, systems and audits built or
led. **The test is the work, not the arithmetic:** does this posting describe
things the candidate has actually done? If yes, keep it whatever the year line
says. Never reject on title alone, a "preferred" qualification, one tool among
several, or a title that sounded wrong.

### Titles lie in both directions

- An in-scope title hiding an out-of-scope job (fictional: a "Business Analyst"
  that is commission-only cold sales).
- An out-of-scope-sounding title hiding the candidate's job (fictional: an
  "Administrator" that is really coordination plus partnership growth).

Record every rejection with the **quoted line** that caused it in
`resume-data/job-search/skipped-with-reasons.md`. A rejection with no quote is an
assumption.

---

## Output contract

Report:

```
BOARD: <name>   FILTERS: <what was set>   SCANNED: <n>
PASS 1 titles kept: <n>   dropped: <n>
PASS 2 shortlist:  <n>    (with comp, region, link, one-line note)
PASS 3 read:       <kept, Strong/Nearly> / <skipped, each with a quoted bar>
```

Write `resume-data/job-search/SHORTLIST.md` — one row per kept role: title,
company, link, fit Strong/Nearly, and the quoted posting line that decided it —
so the queue survives the session. Show it to the user, who chooses what to
pursue. **This skill never applies to anything.**

## Failure modes to watch in yourself

- **Momentum narrowing.** After working several roles of one type, the next scan
  quietly looks only for that type. Re-read the capability list before each
  Pass 1.
- **Summarising into an assumption.** Writing "language X likely required" for a
  posting never opened. If it was not opened, the note is "CHECK — not opened",
  never a verdict.
- **Trusting a past filter.** Any shortlist produced by keyword matching is
  suspect. Re-run Pass 1 by reading.

## Where this sits

Runs **before** the per-application pipeline. A role that clears Pass 3 and that
the user chooses goes to `jd-analyst`.
