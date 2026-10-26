---
name: resume-positioner
description: Run BEFORE writing or tailoring any resume. Decides what the resume is about — the identity a skimming recruiter should infer, the evidence pillars that prove it, and what gets cut. A resume is a compressed evidence architecture, not an argument answering one question, so it needs selection and hierarchy rather than the application writing team. Outputs a Positioning Brief. Does not write bullets.
---

# Resume Positioner

## Why this exists

A QA checklist (`resume-analyser/references/qa-checklist.md`) verifies a draft,
but it cannot decide what the resume is about, what the recruiter should notice
first, which evidence deserves the top third of the page, or whether a
technically impressive bullet is strategically irrelevant. This skill makes
those decisions before any writing starts; the checklist stays as the
verification suite.

## The failure this prevents

**Flattening.** A candidate with many substantial achievements in one role,
presented at equal volume, leaves a recruiter unable to tell whether they are
looking at a support leader, an operations builder, a partner manager, a
training lead or an analytics operator. The honest answer may be "all of
those"; **a resume cannot communicate all of those at equal volume.**

## Procedure

1. **Read the target JD** and the role archetype.
2. **Choose the primary identity** — the one a recruiter should infer in the first
   third of the page. One line.
3. **Choose a secondary identity.** One. Not three.
4. **Choose 3-4 evidence pillars** that prove the primary identity.
5. **Map the top achievements** to those pillars, from `career-bank.md`.
6. **Name the exclusions** — real achievements that will not appear, or will drop
   to one compressed line, because they do not serve this positioning.

## Output contract — the Positioning Brief

```
TARGET:               <role / company / archetype>

PRIMARY IDENTITY:     <what the recruiter should conclude in the top third>
SECONDARY IDENTITY:

EVIDENCE PILLARS:     1.  2.  3.  (4.)

TOP-THIRD CONTENT:    <what earns the summary and the first role's opening bullets>

DEMOTED:              <real achievements compressed to one line>
EXCLUDED:             <real achievements left out entirely, and why>

SKIMMING TEST:        <what job would a recruiter assume this person is applying
                       for, reading for 8 seconds?>
```

Worked example (fictional candidate):

```
PRIMARY IDENTITY:   Customer operations leader who builds structure where none exists
SECONDARY IDENTITY: Customer-facing systems builder
EVIDENCE PILLARS:   1. scaled management scope
                    2. training and quality systems
                    3. operational systems and process building
                    4. measurable service improvement
```

## The summary rule

**The summary states identity plus differentiator. It does not pre-prove
everything.** Stacking five claims into one paragraph is the experience section
doing its own job badly, and it reads as someone ensuring nothing gets missed.

Wrong shape (everything pre-proved):
> "...wrote the first onboarding guide, first QA rubric and first escalation
> process, then led the rollout of a new ticketing workflow... CSAT 3.6 → 4.5;
> first response time 9 min → under 3 min. Joined a 3-person team and now leads
> 18 people across three functions..."

Right shape (identity, then let the bullets prove it):
> "Customer operations leader who builds structure where none exists. Grew a
> 3-person support team into an 18-person, three-function operation, turning
> recurring customer problems into training, quality and operating systems."

## Authority

**Blocks:** yes — no resume writing or tailoring before a Positioning Brief exists.

**Tie-breaker:** the JD decides what is relevant; `career-bank.md` decides what is
true; this role decides what is *prominent*.

## Hands off to

`resume-content-optimizer` for the writing, working at section and page level
rather than bullet-by-bullet, then `resume-analyser` and its QA checklist as the
verification suite.
