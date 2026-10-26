---
name: resume-profile-manager
description: Use when a candidate needs resumes for more than one type of role — "I need a resume for PM roles and a different one for data roles", "build me a resume for X but tailored a different way for Y". Manages a single career bank (all real experience, tagged) and per-role-archetype profiles that each select/emphasize a different subset of it. Do not use this to write bullets or tailor to one specific job posting — that's resume-content-optimizer + job-description-analyzer; this skill only decides which experience to foreground for which type of role.
---

# Resume Profile Manager

## Why this exists

A single resume only works for one working profile — the same career history
reads differently depending on whether the target role is "growth PM" or
"data analyst" or "technical PM." Rewriting from scratch per target invites
two failures: real experience gets forgotten because it's not in whichever
resume the candidate happens to be editing, and the tailoring keeps
reinventing (and risks slightly re-fabricating) the same facts differently
each time. This skill fixes both by separating **the facts** (career bank —
one file, exhaustive, never rewritten) from **the framing** (a profile —
which subset and emphasis for one archetype of role).

## Data layout

```
resume-data/
  career-bank.md              <- one master file, see references/career-bank-format.md
  profiles/
    <slug>.md                 <- one per role archetype, see references/profile-format.md
  output/
    <slug>/
      resume.md                <- resume-content-optimizer's output for this profile
      resume.pdf / resume.docx <- pdf-report / resume-docx-export output
      cover-letter.md           <- cover-letter-generator output, if built
```

## Process

### First time (no career bank yet)
1. If the candidate has an existing resume/CV, run `resume-extractor` on it
   first to seed content — don't start from a blank page if real content
   already exists somewhere.
2. Build/expand `resume-data/career-bank.md` per
   `references/career-bank-format.md` — interview the candidate for
   achievements the old resume didn't have room for. The bank should end up
   more complete than any single resume derived from it.

### Defining a profile
1. Ask the candidate what type(s) of role they're targeting — don't infer
   silently from the career bank; a candidate might want to pivot toward
   something their history doesn't obviously suggest.
2. Write `resume-data/profiles/<slug>.md` per
   `references/profile-format.md` — `priority_tags` must use tags that
   actually exist in the career bank (check, don't assume).
3. If the candidate has a real job posting on hand for this profile, run
   `job-description-analyzer` on it and fold genuinely relevant keywords
   into `priority_tags` — but a profile should still make sense if that one
   posting disappeared; don't over-fit a profile to a single JD (that's what
   per-application tailoring in `resume-content-optimizer` is for).

### Building a resume for a profile
1. Run the selector:
   ```bash
   python3 ".claude/skills/resume-profile-manager/scripts/select_for_profile.py" resume-data/career-bank.md resume-data/profiles/<slug>.md
   ```
   This ranks every career-bank bullet by tag overlap with the profile —
   real, reproducible ranking, not the model re-skimming the whole history
   each time.
2. Hand the ranked bullets + the profile's `summary_angle` to
   `resume-content-optimizer` to draft `resume-data/output/<slug>/resume.md`.
   High-scoring bullets lead; zero-score bullets are candidates to omit, not
   automatically cut — check whether a zero-score bullet is still needed for
   basic coverage (e.g. explaining an employment gap) even if it doesn't
   match this profile's emphasis.
3. This is normally invoked as one step of `resume-builder`'s full pipeline,
   not run standalone, except when the candidate only wants to update
   profiles/selection without regenerating output yet.

## Multiple profiles = repeat the last two steps per profile

Each profile's `resume-content-optimizer` pass and render is independent —
`resume-builder` loops "build a resume for a profile" once per profile,
sharing the one career bank. A change to career-bank.md (a new job, a new
metric) should prompt re-running selection for every existing profile, not
just the one being actively edited — otherwise profiles quietly go stale
relative to each other.
