# Five-persona critique framework

Adapted from ARPeeketi/claude-resume-kit's `critique_framework.md` — the one
genuinely structured critique method found across 8 public resume skills
surveyed for this project (see SKILL.md "Why this exists"). Run as a single
pass: read the resume once, then answer as each persona in turn, in this
order (fastest reader first).

For each persona, give a verdict on the scale shown, plus 1-3 concrete
sentences citing specific lines/bullets — not generic praise or criticism.

## 1. ATS bot (0 seconds — parses text, doesn't "read")
Verdict: `PARSES CLEAN` / `PARSING RISK` / `FAILS TO PARSE`
Check only what a parser checks: single column vs. multi-column/tables,
standard section headers vs. creative ones, contact info in body text vs.
header/footer, consistent date formatting, no images/icons carrying
information. This persona has no opinion on writing quality — don't let it.

## 2. Recruiter (~10 second skim)
Verdict: `SCREEN IN` / `MAYBE` / `SCREEN OUT`
What lands in a 10-second skim: name, most recent title + company, 2-3
standout numbers, overall visual density (is it a wall of text?). Note the
first thing their eye would catch, and whether it's the thing that should
sell the candidate.

## 3. HR generalist (~30 seconds — checks fit, not depth)
Verdict: `MEETS REQUIREMENTS` / `PARTIAL` / `MISSING REQUIREMENTS`
Does the resume, on its face, meet the stated years-of-experience,
education, and named-tool requirements from the job description? This
persona doesn't judge quality of work, only presence of qualifying facts.

## 4. Hiring manager (~2 minutes — reads for substance)
Verdict: `STRONG FIT` / `WORTH A CALL` / `WEAK FIT`
Do the bullets show impact and ownership, or just activity? Is there
evidence of the specific skills the role needs, demonstrated (not just
listed)? Flag any bullet that describes a task without a result.

## 5. Technical/domain reviewer (~10 minutes — reads for credibility)
Verdict: `CREDIBLE` / `NEEDS VERIFICATION` / `RED FLAGS`
Do the technical/domain claims hang together (tools + scale + outcomes
plausible for the stated seniority and company size)? This is the persona
most likely to catch a fabricated or exaggerated claim — apply it with the
same skepticism a real technical interviewer would.

## After all five

Synthesize, don't average. A resume that a recruiter would screen in but a
hiring manager would call weak is telling you the summary oversells relative
to the bullets — say that explicitly rather than reporting five disconnected
verdicts.

## HR score (banded, not a fake number)

After the five verdicts, count how many landed on the positive outcome
(`PARSES CLEAN`, `SCREEN IN`, `MEETS REQUIREMENTS`, `STRONG FIT`,
`CREDIBLE`) versus the negative one (`FAILS TO PARSE`, `SCREEN OUT`,
`MISSING REQUIREMENTS`, `WEAK FIT`, `RED FLAGS`) versus the middle
(`PARSING RISK`, `MAYBE`, `PARTIAL`, `WORTH A CALL`, `NEEDS VERIFICATION`).
Report a band, always alongside the five individual verdicts, never instead
of them:

- **Strong** — 4-5 personas positive, 0 negative
- **Moderate** — 2-3 positive, or any mix without a negative verdict
- **Weak** — any negative verdict from Recruiter, HR generalist, or Hiring
  manager (these three gate the "would this resume advance" question; a
  single `RED FLAGS` from the technical reviewer or `PARSING RISK` from the
  ATS bot should be called out but doesn't alone drop the band to Weak)

This band is a **transparent tally of the five judgment calls above**, not a
new invented number — always show the five verdicts it was tallied from.
Keep it visually and textually separate from `analyze_resume.py`'s ATS
score (see SKILL.md) — one is code-computed, one is a structured count of
LLM judgment, and merging them back into a single score is exactly the
mistake this project was built to avoid (see SKILL.md "Why this exists").
