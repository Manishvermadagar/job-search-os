---
name: resume-analyser
description: Use when the user wants an existing resume critiqued, scored, or checked against a job description — "review my resume", "how good is this resume", "grade this resume", "does this pass ATS", "check my resume against this job posting". This is an analysis skill (input a resume, get a critique) — for writing or rewriting resume content, use resume-content-optimizer instead; for producing the final PDF, use pdf-report.
---

# Resume Analyser

## Why this exists

Eight public Claude/Claude-Code resume skills were surveyed before writing
this one (dabydat/resume-builder-skill, ARPeeketi/claude-resume-kit,
SankaiAI/ats-optimized-resume-agent-skill, Paramchoudhary/ResumeSkills,
vibewith-brent/claude-resume-skills, nipungakkhar/ats_resume_optimizer,
erichowens/cv-creator, phuryn/pm-skills' review-resume). Every one of them
that claims to produce an "ATS score" — including one whose README claims a
verified 95/100 on a 2,000-line scoring engine — turned out, on reading the
actual code, to have no scoring code at all: the number is the LLM narrating
a plausible-looking figure into a template. `erichowens/cv-creator`'s own
`references/resume-protocol.md` literally spells out a 100-point rubric in
prose for the model to *apply itself while narrating* — there is no
`def score(resume)` anywhere in that repo.

This skill fixes that by splitting the analysis into two kinds of claims and
never blurring them together in the output:

1. **Computed facts** — from `scripts/analyze_resume.py`, a real script that
   counts things (banned AI-sounding phrases, bullets missing a metric,
   keyword overlap against a pasted job description, missing sections). If
   this script says 6 banned phrases were found, that's an exact count you
   can verify by re-running it, not an estimate.
2. **Judgment calls** — the 5-persona critique in
   `references/critique-personas.md` (adapted from claude-resume-kit, the
   one repo surveyed with a genuinely structured — not just numeric —
   critique method). This is real LLM judgment and should be presented as
   judgment, not dressed up as a score.

Never merge these into one fake overall number. A resume analysis that says
"78/100" without saying which 22 points are code-checked deductions and
which are subjective is exactly the failure mode this skill exists to avoid.

## How to run an analysis

1. Get the resume as a text/markdown file (ask the user to paste it or point
   to a file — if only a PDF exists, extract text first with `pdftotext
   -layout`, don't eyeball a rendered PDF for this step).
2. If a job description was provided, save it to a file too.
3. Run the computed checks, passing `--doctype cv` for an extended CV so
   length isn't penalized (see "Two scores" below for what `--doctype`
   changes):
   ```bash
   python3 ".claude/skills/resume-analyser/scripts/analyze_resume.py" <resume.md> [--jd job_description.txt] [--doctype resume|cv]
   ```
   Report these results verbatim — banned-phrase hits with line numbers,
   third-person-pronoun hits with line numbers (resumes omit the subject
   entirely — "Directed X", never "He directed X"; this is a structural
   convention violation, not a style nit, and is code-checked because it's
   100% mechanically detectable), bullet/metric counts, missing sections,
   keyword overlap % and the actual missing-keyword list, and the ATS score
   breakdown the script prints at the end. Don't round up, don't
   editorialize into a different number.
4. Read `references/critique-personas.md` and run the 5-persona pass on the
   resume text yourself (this part is not scriptable — it requires reading
   and judgment). Report each persona's verdict with a specific citation
   from the resume, not generic praise/criticism, then roll the five
   verdicts into the HR band (Strong/Moderate/Weak) per that file's "HR
   score" section.
5. **Cross-verify against real-world resume/CV conventions**, not just this
   project's own rules — read the draft as a skeptical outside reader would:
   does it sound like a real professional wrote it, or like a template
   filled in? Specifically check for: meta-commentary that explains a
   framing choice instead of just stating the accomplishment (a resume bullet
   should never read like a note-to-self about why it's phrased that way),
   generic corporate-speak that could describe any candidate, and phrasing
   lifted verbatim from a conversation about the resume rather than written
   as resume prose. This step exists because a resume built up through many
   rounds of conversational correction can end up sounding like a transcript
   of those corrections rather than a resume — catch that here.

   Run through `references/qa-checklist.md` explicitly as part of this
   step — it's a standing list of failure modes that commonly ship
   in drafted resumes (each with the fix and why), not a generic
   reminder. Treat every item as a required check, not optional context.
   `resume-data/resume-qa-ledger.md` is the append-only log this checklist
   is distilled from — add a new entry there (and fold the generalizable
   lesson into the checklist) any time a genuinely new failure mode is
   found, so it gets caught automatically on every future build instead of
   only in the conversation where it was noticed.
6. Synthesize: lead with anything the script flagged as an outright problem
   (banned phrases, missing sections, low ATS score components — these are
   objectively fixable), then the persona synthesis and HR band, then the
   cross-verification findings from step 5, then concrete next actions
   ordered by effort/impact.

## Two scores, never merged

- **ATS score** (`analyze_resume.py`'s printed breakdown, 0-100) — fully
  code-computed from sections present, banned-phrase count, bullet/metric
  ratio, weak-verb count, and length fit. This measures parseability and
  keyword hygiene, not quality of the work described. Always show the
  component breakdown, not just the total.
- **HR score** (Strong/Moderate/Weak band from the 5-persona critique) —
  structured LLM judgment, not code. Always show the five underlying
  verdicts alongside the band.

Report both, clearly labeled, side by side if useful — but never average or
combine them into one number. See "Why this exists" above for why that
specific failure mode is the one this skill was built to avoid.

## Reducing conversational bias

If this analysis is being run on a resume that went through several rounds
of user feedback in the same conversation, prefer running steps 4-5 via a
fresh subagent that has not seen that conversation and is given only the
resume file (and the career-bank/profile source files for fact-checking) —
not a summary of what the user said. A reviewer who watched the whole
back-and-forth tends to grade the resume against "did it address the
feedback" rather than "does this read well on its own," which is a
different and weaker bar.

## Relationship to `humanizer`

Not overlapping, deliberately narrower here: `humanizer` is a broad style
pass run *during drafting* in `resume-content-optimizer` (rhythm, sentence
variety, the full range of AI-writing tells). This skill's banned-phrase
scan is a much smaller, code-enforced, always-run final gate on an already-
drafted resume — a safety net for the specific words on
`resume-content-optimizer`'s list, not a substitute for a full humanizer
pass. If this skill flags banned phrases on a resume that never went through
`humanizer`, that's the signal to run `humanizer` on it before further
manual fixes.

## What this skill deliberately does not do

- **No invented overall score.** If the user wants "one number," give the
  keyword-overlap percentage (it's the only genuinely computed one) and say
  explicitly that the rest is qualitative.
- **No JD keyword extraction via LLM guessing.** `keyword_overlap()` in the
  script uses a plain, auditable rule (terms appearing 2+ times in the JD) —
  intentionally dumber than an LLM's judgment, but reproducible. If it
  misses an obviously important single-mention keyword (e.g. a specific
  certification named once), call that out manually — don't silently patch
  the rule per-run.
- **Doesn't rewrite the resume.** Handing back critique is the job; if the
  user wants the content fixed, switch to `resume-content-optimizer`.

## Extending the checks

`BANNED_WORDS` / `BANNED_PHRASES` in `scripts/analyze_resume.py` are a
starting list (merged from claude-resume-kit and SankaiAI's validator, with
SankaiAI's soft warning upgraded to a hard fail here). If a new AI-sounding
pattern turns up repeatedly in drafts, add it there — extend the list, don't
special-case it in the SKILL.md instructions, so the check stays reproducible
outside the conversation too.
