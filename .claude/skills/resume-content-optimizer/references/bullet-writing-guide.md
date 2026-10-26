# Bullet writing: XYZ formula + AI-fingerprint avoidance

## The XYZ formula
Every experience bullet: **"Accomplished [X] as measured by [Y], by doing
[Z]"** — result first, metric second, method third. In practice this reads
more naturally reordered as **[Action verb] + [what you did] + [how] +
[result, with a number]**:

> Weak: "Responsible for managing the deployment pipeline"
> Strong: "Cut deployment time from 45 to 8 minutes by migrating CI from
> Jenkins to GitHub Actions and parallelizing the test suite"

If a bullet has no number and none is obtainable, use proxy scale language
instead of a fabricated metric — see `metric-excavation.md`.

## Weak bullet starts to eliminate
"Responsible for", "Helped", "Worked on", "Assisted with", "Involved in",
"Duties included" — these describe presence, not impact. Replace with the
actual action verb for what was done (see the seniority/function verb banks
below).

## AI-fingerprint avoidance
Sourced from ARPeeketi/claude-resume-kit's `ai_fingerprint_rules.md` — the
only one of 8 surveyed resume skills with an explicit list for this, and
enforced in code (not just prompted) by `resume-analyser`'s
`analyze_resume.py` banned-phrase scan.

**Banned words** (LLM-resume tells): delve, tapestry, multifaceted, pivotal,
leverage, utilize, spearhead, synergy, robust, seamless, cutting-edge,
game-changer, paradigm, holistic, bespoke, unparalleled.

**Banned phrases**: "responsible for", "passionate about", "results-driven",
"proven track record", "team player", "detail-oriented", "hard worker",
"go-getter", "think outside the box", "I am uniquely positioned to...",
"It's not just X — it's Y" constructions, "In today's fast-paced [industry]".

**Structural tells to avoid**: more than 2 em-dashes in the whole document,
bullets that all end in an "-ing" participial phrase, uniform sentence
length (real writing has variance — vary bullet length within a role rather
than making every bullet the same length).

Run `resume-analyser`'s script against the draft before calling it done —
don't rely on remembering this list while writing.

## Action verb banks (by function)
Use a verb that actually matches the level of ownership — a "led" for work
you didn't lead is the fabrication risk in the other direction, not just
under-selling.

- **Built/created**: architected, built, developed, designed, launched,
  established, founded, engineered, authored, created
- **Improved/optimized**: reduced, increased, improved, optimized,
  streamlined, accelerated, cut, boosted, strengthened, refined
- **Led/managed**: led, directed, managed, coordinated, mentored,
  supervised, orchestrated, drove, spearheaded (⚠ banned above — use "led"
  or "drove" instead)
- **Analyzed/solved**: analyzed, diagnosed, resolved, investigated,
  identified, evaluated, audited, forecasted
- **Communicated/influenced**: presented, negotiated, persuaded,
  facilitated, authored, published, trained, onboarded

## Weak verbs to always replace
"Did", "made", "got", "worked", "handled", "dealt with", "used" — these are
placeholders, not real answers. If the strongest verb you can honestly write
is "used," the bullet is missing the actual action (what did using it
accomplish?).
