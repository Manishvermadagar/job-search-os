# Career bank format

The career bank (`resume-data/career-bank.md` by convention — see SKILL.md)
is the single source of truth for a candidate's real work history: every
role, every achievement, written once, tagged, never rewritten per-resume.
Individual resumes are *views* into this file, not separate drafts that
drift from it.

## Format

```markdown
# Career Bank

## Acme Corp — Senior Product Manager | Jan 2023 – Present
tags: product-management, saas, b2b, growth, leadership

- Cut onboarding drop-off from 38% to 12% by redesigning the first-run flow, based on funnel analysis across 40K+ new signups [tags: growth, onboarding, data-analysis]
- Led a team of 4 engineers and 1 designer to ship a self-serve billing portal, reducing support tickets by 22% [tags: leadership, team-management]

## Beta Inc — Product Manager | Jun 2020 – Dec 2022
tags: product-management, mobile, b2c

- Launched the mobile app's notification system, increasing 7-day retention by 9 percentage points [tags: growth, mobile]
```

- `## Company — Title | Dates` starts a role.
- `tags: ...` right after the role header applies those tags to every bullet
  under that role (role-level context — e.g. "this whole role was B2B SaaS").
- Each bullet can carry its own `[tags: ...]` suffix for bullet-specific
  relevance on top of the role tags.
- Write every real bullet you have for a role here, even ones that won't fit
  a 1-page resume — the bank is allowed to be long. Trimming happens at
  profile-selection time (`select_for_profile.py`), not here.

## Building it for the first time

If the candidate has an existing resume/CV, use `resume-extractor` first to
pull its content in, then expand: for each bullet, ask what else was true
about that role that the old resume didn't have room for. The bank should
end up **larger** than any single resume that gets built from it — that's
the point.

While expanding, actively ask for **business-impact metrics** specifically
— retention/churn, revenue or account value, SLA compliance, cost savings,
productivity per person/agent — not just the operational metrics (team
size, CSAT, response time, ticket volume) that tend to come up first.
Operational metrics prove execution; business-impact metrics are what
separates a function-manager resume from an operations/business-manager
one (see `resume-content-optimizer/references/
positioning-and-prioritization.md` #6). If an achievement plausibly saved money
or drove a business outcome (e.g. building something in-house instead of
buying/licensing it), ask for the real comparison number before treating
that gap as unfillable — never estimate or invent one if the candidate
doesn't have it.

## Tag taxonomy

Don't over-engineer a fixed tag vocabulary up front. Useful tag categories in
practice: function (`product-management`, `data-analysis`, `sales`),
domain/industry (`saas`, `healthcare`, `fintech`), skill
(`sql`, `stakeholder-management`, `figma`), and scope (`leadership`,
`individual-contributor`, `0-to-1`). Reuse existing tags before inventing a
near-duplicate (`leadership` vs `team-lead` vs `managed-team` — pick one and
stay consistent) — `select_for_profile.py`'s matching is exact-string, not
fuzzy, so tag drift silently breaks selection.
