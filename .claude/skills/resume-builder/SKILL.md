---
name: resume-builder
description: Use when the ask is the end-to-end goal — "build me a resume", "I need resumes for X and Y type roles", "create/update my resume" — rather than one isolated step. This is the master orchestrator: it decides which of the nine resume sub-skills to invoke and in what order, including looping the pipeline once per target role profile for candidates who need more than one resume. Don't use this for a single narrow ask that already names its skill directly (just critiquing one resume → resume-analyser; just writing a cover letter → cover-letter-generator).
---

# Resume Builder (master orchestrator)

## Why this exists, and why it's nine skills instead of one

Many resume tools collapse "analyze," "write," "tailor," and "render" into
one undifferentiated prompt. That leaves no real scoring engine, no
separation of fact from framing, and no way to serve a candidate who needs
more than one resume without starting over. This resume skill set is
deliberately split so each piece can be reused, tested, and
trusted independently:

| Skill | Job |
|---|---|
| `resume-extractor` | Existing PDF/DOCX → clean text |
| `resume-profile-manager` | Career bank (facts) + profiles (framing per role archetype) + selection |
| `job-description-analyzer` | One posting → tiered keywords + requirements |
| `resume-content-optimizer` | Writes/tailors bullets, XYZ formula, metric excavation |
| `humanizer` | Strips AI-writing patterns, preserves every fact |
| `resume-analyser` | Code-enforced self-check gate + qualitative critique |
| `resume-visual-format` | The design system both renderers implement — typography, section architecture, emphasis budget, page-break rules. Read before rendering or before changing any style token. |
| `pdf-report` (resume mode) | PDF render |
| `resume-docx-export` | DOCX render |
| `cover-letter-generator` | Companion cover letter per application |
| `ai-cross-reviewer` | Optional: second opinion from a different model (Codex CLI, or ChatGPT by copy-paste) on an already-drafted resume+CV, fact-checked against the career bank before use |

See `references/pipeline-diagram.md` for how data flows between them.

## Step 0: figure out what's actually being asked for

Ask (or infer from context) before running anything:

1. **Does a career bank already exist** (`resume-data/career-bank.md`)? If
   not, this is a first-time build — start from Phase A below.
2. **Does the candidate need one resume, or more than one?** If they work
   toward genuinely different role types (e.g. "PM roles and also data
   roles"), this is a multi-profile build — Phase B runs once per profile.
3. **Is this "build my standing resume(s)" or "tailor for this specific job
   I'm applying to right now"?** The former stops after Phase B/C. The
   latter also runs Phase D against one posting, on top of an
   already-selected profile — don't rebuild profiles/selection just to
   apply to one job.

## Phase A — Foundation (once per candidate, not once per resume)

1. If an existing resume file exists (PDF/DOCX), run `resume-extractor` on
   it first.
2. Run `resume-profile-manager` to build/expand `resume-data/career-bank.md`
   — this should end up with more content than any single resume will use.
   Skip re-running this phase on later invocations unless the candidate has
   new experience to add.

## Phase B — Define profile(s)

For each distinct role type the candidate is targeting, use
`resume-profile-manager` to write a `resume-data/profiles/<slug>.md`. A
candidate targeting one type of role gets one profile; do not manufacture
extra profiles that would produce near-identical resumes — see that skill's
"when to create a new profile vs. reuse one."

## Phase C — Build a resume, once per profile

For **each** profile from Phase B, run in order:
1. `resume-profile-manager`'s `select_for_profile.py` → ranked bullets for
   this profile.
2. `resume-content-optimizer` → drafts `resume-data/output/<slug>/resume.md`
   (and, when the candidate's history is too deep for one page, a
   `cv.md` alongside it — see that skill's guidance on when both are
   needed) from the ranked bullets + the profile's `summary_angle`. Draft
   from the career bank and profile file **only** — if this phase is
   reached after a long back-and-forth with the candidate about framing,
   write the draft from the source files, not from memory of the
   conversation; see "Avoid conversational fixation" below. Includes a
   mandatory positioning step (that skill's step 2.5,
   `references/positioning-and-prioritization.md`) — decide the one
   primary identity, the elevated differentiator, and the pillar structure
   *before* writing bullets, not as an afterthought caught in review.
3. `humanizer` → dehumanize the mechanical draft into natural prose,
   preserving every fact. Prefer running this via a fresh subagent that
   sees only the draft (not the conversation) — see
   `resume-analyser/SKILL.md`'s "Reducing conversational bias."
4. `resume-analyser` (self-check mode) → must come back clean (or fixed)
   before proceeding. Report both scores (ATS breakdown, HR band) and the
   cross-pattern-verification findings, not just the banned-phrase count.
5. **Proofread** — a final, fresh read (ideally a subagent that hasn't seen
   the drafting process) checking every claim against `career-bank.md`
   line by line (flag anything unsupported as a fabrication risk, don't
   just trust the draft), and checking that the prose reads like a resume
   a human wrote, not a record of the conversation that produced it. This
   is a distinct step from `resume-analyser`'s automated checks — it's a
   comprehension read, not a pattern scan. Also run through
   `resume-analyser/references/qa-checklist.md` explicitly — a standing
   list of failure modes that have actually shipped in a drafted resume
   before (fabrication-adjacent misses like a headline that doesn't map to
   the JD's real responsibilities, or a dropped profile hedge, are on it
   alongside mechanical ones). Fix anything found before rendering.
6. `resume-visual-format` → **read it before rendering.** It defines the
   Markdown shape both renderers expect (`## Core Competencies` capped at
   10-12 items, `## Tools & Technical` in labelled groups, `### Title —
   Company | Dates`, education entries as compact `###` entries) and the
   emphasis budget (**one primary bold anchor per bullet**, arrows for
   genuine before/after only). A resume drafted without these will render
   correctly but read flat. Treat the design system as settled; implement
   it rather than re-opening it per build.
7. `pdf-report` (resume mode) and/or `resume-docx-export` → render. Arial and
   a 2-page cap are locked defaults, so no flags are needed for a resume; CVs
   and cover letters need `--max-pages 0`. The renderer prints the page count
   and any fit compression it applied, and **warns if the content cannot fit**
   rather than shrinking further or dropping bullets — if it warns, the
   decision about what to cut is the candidate's. Render filenames follow
   `pdf-report`'s naming rule.
8. **Verify the rendered PDF, not the estimate.** Check the real page count
   from the renderer's own output or `pypdf`, never `resume-analyser`'s
   ~550-words/page heuristic — they diverge because real margins and spacing
   don't match a flat word count. Re-check after *every* content edit, not
   just once. Then render a page to PNG and actually look at it, and confirm
   no bullet splits across the page boundary. See
   `resume-analyser/references/qa-checklist.md`.

Repeat steps 1-8 **for the next profile**, sharing the one career bank —
this is the actual mechanism for "a single resume only works for one
profile, so we build several." Report progress per profile as you go rather
than going silent until all are done; a candidate with 3 profiles should see
3 distinct checkpoints.

## Avoid conversational fixation

A resume represents the candidate's **whole career history** — the career
bank — not the conversation that led to building it. If a build happens
after several rounds of the candidate correcting earlier drafts, it's easy
for the next draft to over-index on restating those corrections verbatim
(explaining a framing choice inside a bullet, repeating the candidate's own
phrasing back as if it were resume prose) rather than writing clean,
independent, natural resume content that happens to reflect the corrected
facts. Guard against this directly: when drafting or redrafting, read from
`career-bank.md` and the profile file as the source of truth, and write as
if this were the first draft with the facts already correct — not as a
patch layered on top of the previous one. Delegating the draft and humanize
passes to a fresh subagent (which never sees the conversation, only the
source files) is the most reliable way to guarantee this.

## Phase D — Tailor to one specific application (optional, per job posting)

Only when the candidate has an actual posting to apply to, on top of an
already-built profile resume:
1. `job-description-analyzer` on the posting.
2. `resume-content-optimizer` re-pass: reorder/reword the profile resume's
   existing bullets toward this posting's Tier 1/2 keywords — same
   no-fabrication rules, this is emphasis, not new content.
3. `humanizer` → `resume-analyser` → proofread → render → verify, same as
   Phase C steps 3-8. Save everything in `resume-data/output/<slug>/` for
   this posting, and start from the closest existing resume rather than a
   blank page when one fits the role.
4. Optional: `ai-cross-reviewer` (Mode A) before rendering.
5. If a cover letter is wanted, `cover-letter-generator` now (it needs both
   the tailored resume and the JD analysis).

## Guardrails that apply across every phase

- **No fabrication, ever** — not new experience, not inflated metrics
  without candidate confirmation, not changed job titles. Every sub-skill
  restates this; it isn't optional at the orchestration level either.
- **Don't skip humanizer.** It's tempting to go straight from
  `resume-content-optimizer` to render since the content is "already good"
  — the mechanical tells (rule-of-three lists, "-ing" padding,
  "leveraged synergies") show up specifically in resume-style writing, which
  is why this pipeline runs it unconditionally rather than only when
  something looks obviously robotic.
- **Don't skip resume-analyser's self-check** even when confident the draft
  is clean — it's a five-second script run against real regressions, not a
  formality.
- **Never submit or send.** This pipeline ends at rendered files shown to
  the candidate; the candidate decides where they go.
- **Log mistakes.** When a drafted resume contained an error that reached
  review, record it and the rule that prevents it in
  `resume-data/resume-qa-ledger.md` and fold the rule into
  `resume-analyser/references/qa-checklist.md`.
- **Progress, not silence.** This is a long pipeline; tell the candidate
  which phase/profile is active rather than running everything and
  dumping results at the end.
