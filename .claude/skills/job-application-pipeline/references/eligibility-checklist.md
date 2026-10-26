# Eligibility Checklist — read before scoring any job as fit or not

Run this on the **full posting text**, never on the search-results card. Title,
pay and the "Remote" badge are each individually misleading often enough that
none of them can be trusted alone.

> The `job-selector` skill owns the selection process. This file holds the
> reference detail it applies.

## 0. Which roles count — screen on the work, not the title

Screening on a narrow set of titles over-rejects. List the role families the user
actually targets in `resume-data/standing-preferences.md` (or their profiles in
`resume-data/profiles/`).

| Family | Example titles |
|---|---|
| e.g. Operations | Operations Manager, Operations Coordinator |
| e.g. Customer success / support | Customer Success Manager, Support Lead |
| e.g. Business operations | Business Operations Associate, Chief of Staff |

Also consider titles containing *generalist*, *associate*, *coordinator*,
*specialist*, *process*, *quality*, *delivery*, *implementation* or *onboarding*.

### The rule

> **Do not reject on title. Open the JD.**
>
> Reject only on a **factual bar**: a country or work-authorization requirement, a
> capability `career-bank.md` says the candidate does not have, or pay below
> `salary-thresholds.md`.

### Usually out of scope

Unless the user's profiles say otherwise: commission-only, equity-only, unpaid or
volunteer roles, co-founder postings, internships, and "paid product tester"
listings.

### Titles mislead in both directions

- An in-scope title ("Business Analyst") can hide commission-only sales.
- A clerical-sounding title ("Administrator") can hide a partnerships and
  coordination role that fits well.
- A plausible title ("Technical Product Manager") can carry a hard requirement,
  such as years of prior software engineering, that rules it out.

Only the JD settles it.

## 1. Pay — check the currency, the period and the math

- **Confirm per year vs per month.** A monthly figure read as annual looks far
  too low; an annual figure in another currency can be a real raise.
- **Convert to the user's comparison currency** with a rate looked up for this
  conversion, not remembered. Record the converted figure and the rate and date
  in the tracker note.
- **A figure far outside the plausible range for the role is more likely a
  listing error than a windfall.** Flag it for verification.
- Compare against `salary-thresholds.md`, not against a remembered number.

## 2. "Remote" is not one thing

Read the posting's **hiring-region / location-restriction** field, not the badge.
A "Remote" role can be limited to one country or a short list of countries; a role
can also list the user's region explicitly and be wrongly rejected if only the
badge is read. Do not infer eligibility from the word "Remote" in either
direction.

**Work authorization is a separate field from hiring region**, and often the most
common disqualifier. A broad hiring region can still require "authorized to work
in [country] without sponsorship". Check it explicitly. Also check contract vs
employee status, and whether pay is equity-only.

Some restrictions appear only inside the apply flow, not on the posting page —
see the pipeline's channel-discovery phase.

## 3. The title can misdescribe the role — read the responsibilities

An "Onboarding Specialist" can be a product-management role requiring a specific
degree; a "Customer Success Manager" can be log-reading technical support; an
"Implementation" role can require writing non-trivial SQL unaided. Read what the
person does day to day before deciding it matches.

## 4. Years of experience — read the number

High pay does not imply a matching seniority bar, and vice versa. Read the stated
years every time and compare with the career bank.

## 5. Domain specificity

Some roles need a specific regulated or specialist vertical (for example, fund
operations under a particular regulator) that general operations experience does
not cover, however well the title reads.

## 6. Technical ceiling

Compare any technical requirement with the honest technical-depth statement in
`career-bank.md`. A requirement above that ceiling is a real mismatch; report it
plainly rather than calling it "a stretch worth trying".

## 7. Unusual application mechanics — note, don't skip

- "Applications on [board] will not be reviewed — apply via this link": follow
  the posting's instructions, not the board's default button.
- Unusual requests in the application (a personality type, a specific subject
  line, a code word): surface them to the user; do not silently comply or ignore.
- A required external assessment before review: flag it as a different process.

## 8. Is anyone hiring?

- A dead listing can still load with the full JD. Look for the board's explicit
  "no longer available" text.
- Check whether the employer's own careers page lists the role. "No open roles"
  there while the board shows it open is a warning.
- Check the website the employer itself listed: real content, not a parking page,
  not registered days before the posting.

## Applying this checklist

When a role moves from "new" to "JD pulled" in a tracker, pull the full posting
and check items 1–8 explicitly before writing the eligibility note. A role whose
title and pay look attractive but has not been checked should say "JD not yet
pulled", not carry a provisional score.
