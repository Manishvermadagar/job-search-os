---
name: resume-content-optimizer
description: Use when writing a new resume from scratch or rewriting/tailoring resume content — "help me write my resume", "tailor my resume to this job", "rewrite these bullets", "optimize my resume for ATS". This is a content/writing skill — for critiquing an already-written resume, use resume-analyser instead; for producing the final PDF, use pdf-report.
---

# Resume Content Optimizer

## Why this exists

Built after surveying 8 public Claude/Claude-Code resume skills for real,
usable methodology rather than picking one by star count or marketing copy.
The best-sourced one (dabydat/resume-builder-skill) ships a `SOURCES.md` that
cites Harvard's career guide, the r/EngineeringResumes wiki, and Gergely
Orosz's "The Tech Resume Inside Out" for every formatting rule it makes, and
explicitly flags where those sources disagree (e.g. 1-page-always vs.
2-pages-for-seniors). That rigor is worth keeping. Two things it's missing
were pulled from elsewhere: ARPeeketi/claude-resume-kit's AI-fingerprint
banned-word list (LLM-written resumes have tells — "delve," "leverage,"
"spearhead" — that a human reader and increasingly an AI-detection-aware
recruiter will notice), and nipungakkhar/ats_resume_optimizer's metric-
excavation technique (a structured way to convert a vague bullet into a real
number instead of leaving it vague or inventing one).

One thing was deliberately left out: nipungakkhar's skill permits changing a
candidate's actual job title to match a target posting ("Marketing
Executive" → "Digital Marketing Manager"). That's a resume-fraud gray area,
not a practice to carry forward — see "Hard rules" below.

## Process

1. **Gather inputs.** If the candidate has multiple target role types,
   inputs come from `resume-profile-manager` — ranked career-bank bullets
   for this profile plus its `summary_angle`, not a fresh interview each
   time. For a single-profile candidate or first-time content, gather work
   history, education, target role, and domain context per role directly.
   Generic bullets come from missing this step, not from bad writing.
2. **Structure.** Read `references/ats-formatting-rules.md` for section
   order and formatting. Skills-first for technical roles, Experience-first
   otherwise; Education moves to the bottom past 3 years of experience.
2.5. **Position before writing bullets.** Read
   `references/positioning-and-prioritization.md` and decide, explicitly:
   the one primary identity the summary will sell (not two co-equal
   categories), which single achievement is the differentiator and gets
   elevated with real proof bullets in the resume itself (not just the
   CV), and which 3-4 pillars the rest of the content organizes around.
   Getting this wrong is invisible to every code check and easy to miss
   even in a structured AI review, so treat this as a required step, not
   something to catch later.
3. **Write content.** Read `references/bullet-writing-guide.md` and apply
   the XYZ formula to every bullet. Where a bullet has no number, run
   `references/metric-excavation.md`'s question categories with the
   candidate before shipping a vague bullet. While excavating metrics,
   also actively check for missing **business-impact** metrics (retention,
   revenue, SLA, cost savings) per
   `positioning-and-prioritization.md` #6 — ask the candidate for the real
   number if a plausible achievement has one but it isn't in
   `career-bank.md`; never invent one.
4. **Tailor to a job description** (if one was provided): run
   `job-description-analyzer` on it rather than eyeballing keywords inline,
   then reorder and reword existing bullets to surface what its Tier 1/2
   keywords call for — do not fabricate experience that isn't there to fill
   a gap. Use both acronym and spelled-out forms of key terms (e.g. "CI/CD"
   and "continuous integration/continuous deployment") since either form
   might be the one an ATS keyword match looks for.
5. **Humanize.** Run the drafted content through `humanizer` before the
   self-check below — resume bullets are exactly the genre that reads as
   mechanically AI-written by default (uniform "-ing" phrase padding, rule-
   of-three skill lists, "leveraged synergies to..." constructions).
   Preserve every fact, metric, and date; humanizer changes phrasing and
   rhythm, never content.
6. **Self-check before handoff.** Run `resume-analyser`'s
   `scripts/analyze_resume.py` against the humanized draft — it's the same
   banned-phrase list this skill uses, enforced as a real scan instead of
   the model trying to remember not to write "leverage." Fix anything it
   flags before treating the draft as final.
7. **Hand off for output.** Once content is final, use `pdf-report`'s
   resume mode and/or `resume-docx-export` to render the document(s) — this
   skill only writes content, it does not lay out or render. If a cover
   letter is also needed, hand off to `cover-letter-generator`.

## Hard rules (do not compromise these for a better JD match)

- **Never fabricate experience, employers, dates, or credentials.**
  Reordering and rewording real experience to foreground what's relevant is
  tailoring; inventing experience is not.
- **Never change a job title to match a target posting.** Reflect the
  actual title held; if the work maps to a different common title, say so
  in a parenthetical or a bullet ("Marketing Executive — functioned as team's
  primary digital campaign lead") rather than rewriting the title itself.
- **No unconfirmed metrics.** An estimate from metric-excavation only goes
  into the final draft after the candidate confirms it.
- **No banned AI-fingerprint words/phrases** — see
  `references/bullet-writing-guide.md`, enforced by the analyser script.
