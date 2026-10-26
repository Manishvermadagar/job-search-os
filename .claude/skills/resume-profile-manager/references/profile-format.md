# Profile format

A profile is a target role archetype — not a single job application. One
candidate might need 2-4 profiles total (e.g. "Growth PM, B2B SaaS" and
"Technical/Platform PM" are different enough resumes; two SaaS companies'
near-identical PM postings are the *same* profile, just tailored further
with `job-description-analyzer` at apply time).

Stored at `resume-data/profiles/<slug>.md` by convention.

## Format

```markdown
---
title: Growth-Focused Product Manager (B2B SaaS)
target_titles: Senior Product Manager, Growth PM, Product Lead
target_industries: B2B SaaS, Marketplace
priority_tags: growth, data-analysis, leadership, saas, b2b
summary_angle: Growth-focused PM with a bias for experimentation and quantified impact, comfortable owning the funnel end to end.
---

Notes: lead with the onboarding and A/B testing work; downplay the early
data-analyst role except where it supports the "data-driven" framing.
```

- `priority_tags` is the only field `select_for_profile.py` reads — it must
  match tags actually used in `career-bank.md` (see that file's taxonomy
  note on tag drift).
- `summary_angle` isn't decoration — hand it to `resume-content-optimizer`
  as the frame for the resume's summary/profile section so it isn't
  generic.
- Free-text notes below the frontmatter are for judgment calls a tag can't
  capture (de-emphasize something, don't fabricate a new tag just to force
  it in).

## When to create a new profile vs. reuse one

Same function, similar seniority, similar industry → reuse the profile,
tailor further with `job-description-analyzer` per posting. Different
function (PM vs. Data Analyst), meaningfully different seniority (IC vs.
manager), or different industry framing the candidate wants to lead with →
new profile. When unsure, ask the candidate directly which roles they're
actually applying to rather than guessing from the career bank alone.
