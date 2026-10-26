# Resume QA Checklist

A standing list of failure modes that commonly ship in drafted resumes. Each
item names the check and the fix. When a genuinely new failure mode is found,
log it in `resume-data/resume-qa-ledger.md` first, then fold the generalizable
lesson into this file so it is checked automatically on every future build.

Run through this list explicitly during `resume-analyser`'s cross-verification
step and `resume-builder`'s proofread. Treat every item as a required check,
not optional context.

## Code-checked (run the script, don't eyeball)

- [ ] **Zero third-person pronouns** (he/his/him/himself/she/her/hers/herself/
  they/their when referring to the candidate). Resumes omit the subject
  entirely: "Directed X," never "He directed X." `analyze_resume.py` checks
  this. If the script reports any hits, fix them; don't wave them past because
  the surrounding prose "reads fine."
- [ ] **Zero banned AI-sounding words/phrases**, enforced by
  `analyze_resume.py`'s `BANNED_WORDS`/`BANNED_PHRASES`. Run the script even
  when the draft already went through `humanizer`.
- [ ] **Rendered PDF page count matches intent**, checked with
  `pdfinfo <file>.pdf | grep Pages`, not `analyze_resume.py`'s word-count
  estimate. Real margins and spacing diverge from a flat words-per-page
  heuristic. Re-check after **every** content edit to a supposedly finished
  document; adding one keyword can push it onto another page.
- [ ] **No leaked markup in the rendered PDF**:
  `pdftotext -layout <file>.pdf - | grep -E "<b>|\*\*|&lt;"` returns nothing.

## Visual-only (text extraction cannot catch these; render to PNG and look)

- [ ] **Wrapped (2+ line) bullets have a real hanging indent**, with
  continuation lines aligned under the bullet text, not under the glyph.
  Extracted text looks correct either way. Render at least one page with a
  wrapped bullet to PNG and check alignment before treating any PDF as final.

## Phrasing that costs credibility

Each item is a phrasing defect, not a factual one. Fix by deleting or softening
words, never by deleting evidence.

- [ ] **No phrase whose only job is to say the achievement was impressive.**
  Ban list: "unprompted", "outside role scope", "single-handedly", "despite no
  support", "went above and beyond", "for the first time" where the sentence
  already says "the first". Example: *"Audited a vendor's invoices, unprompted
  and outside my scope, finding 30% overbilling"*: the number already proves
  initiative. If an achievement needs the qualifier to land, rewrite the bullet.
- [ ] **No verb claiming more credit than the candidate can defend.** "Grew the
  team into a 40-person department" implies sole credit; "helped scale the team
  to 40" is defensible and loses nothing. Check every verb attached to an
  outcome larger than one person.
- [ ] **No asserted causation the analysis doesn't support.** "Benchmarked
  competitors *to explain why* growth lagged" claims proof; "to identify factors
  behind the growth gap" is what a comparison supports. Watch "because", "which
  caused", "to explain why", "proving that".
- [ ] **No sensitive third-party detail, even when true.** Never name another
  party's credentials, personal data, or legal exposure. Ship the competency
  ("identified and escalated a client data exposure"), not the specifics.
- [ ] **No subjective qualifier where an objective one exists.** "a
  higher-stakes tier" → "a higher-accountability tier".
- [ ] **No restated idea inside one bullet** ("the team's first standard ...
  for the first time").
- [ ] **No project-documentation voice.** "Solved a fragmentation problem
  first:" narrates a work log; "Unified fragmented client records across three
  tools" states the outcome. Lead with what changed.
- [ ] **Section labels describe everything inside them.** A section titled
  "Analytics" that also lists ticketing and chat tools should be "Analytics &
  Tools".

## The career bank is a record, not pre-cleared external copy

- [ ] **Before any career-bank phrase ships, ask whether it states an
  observation or a conclusion**, and separately whether it exposes a third
  party. "Billing fraud" is a legal conclusion; "billing discrepancies" is an
  observation. The bank records specifics; the resume ships the capability the
  specifics evidence.
- [ ] **When a fact is true, useful internally and wrong to send, flag it inline
  in `career-bank.md`** with the approved external phrasing, so the next draft
  reads the rule where it reads the fact.

## Tools and skills lines get audited like bullets

- [ ] **Every tool named traces to something the candidate actually did.** The
  tools line is the lowest-attention line in the document and therefore the
  highest-risk. Keep a zero-exposure list in `career-bank.md` and check it.
- [ ] **A reviewer flagging a removed tool as an "accidental content change" is
  not evidence it should come back.** Reviewers cannot see the candidate's
  corrections. Check the zero-exposure notes before restoring anything.

## Manual read (a fresh, skeptical read, not the drafting agent grading itself)

- [ ] **No conversational leakage.** A line should never rebut an invisible
  critic ("a combined role, not a narrower title"). If a sentence only makes
  sense with context the reader lacks, cut it and state the fact plainly.
- [ ] **No overclaimed personal technical or domain understanding.** If the
  candidate directed or reviewed work rather than understanding the underlying
  concepts, say that. Never imply they could defend concepts under interview
  questioning unless they can. Check the career bank's honesty notes.
- [ ] **Headline achievement is mapped against the JD's responsibility bullets,
  not against which achievement sounds most impressive.** Re-read the JD
  responsibility list line by line and lead with the achievement that matches
  it most directly.
- [ ] **Every hedge in the profile notes survived into the final text.** Diff
  the final text against the profile file's notes; drafting passes smooth hedges
  ("adjacent", "exposure to") into flat fact.
- [ ] **Basic facts (company name, exact title, dates, business model) are
  verified against an authoritative source** before deep content work. A wrong
  fact invented during drafting spreads as easily as one in the career bank.
  When a correction lands, fix `career-bank.md` if needed and propagate the fix
  to every file carrying the claim, not just the one being worked on.
- [ ] **No stray em dashes in prose.** Structural `### Title — Company | Dates`
  headers are fine (the renderer's delimiter). Re-check after any edit made
  after the humanizer pass.
- [ ] **A true duration isn't attached to the wrong scope.** "Six years of team
  leadership" is wrong if the tenure is six years but the leadership role began
  last year. When a sentence pairs a duration with a scope, check the scope held
  for the full duration.
- [ ] **Combined metrics don't merge two time periods into one event.** If the
  career bank time-scopes two figures separately, keep them separate or make the
  timeline explicit.
- [ ] **Content from an external AI review is fact-checked against
  `career-bank.md` line by line.** External models asked to "improve" a resume
  fabricate metrics to fill perceived gaps. Never paste a rewritten section in
  directly; redraft genuine improvements through `resume-content-optimizer` →
  `humanizer` → `resume-analyser`.
- [ ] **Ask: "what job title would a skimming recruiter assume, reading top to
  bottom?"** A resume can pass every check while describing the functions
  managed more clearly than the scope owned. Verify the summary and the lead
  bullet of each role reinforce one primary identity.
- [ ] **Run the full `resume-content-optimizer/references/positioning-and-prioritization.md`
  checklist**: internal-authority bullets crowding out impact, an under-proved
  differentiator, niche work framed by its niche name, and unprioritized "proof
  dump" resumes.

## Evidence versus commentary

**The common AI resume failure is argument density, not fabrication.** State
action, context and result, then stop; the reader supplies the interpretation
and therefore believes it. When the resume argues its own significance, trust
drops.

- [ ] **When a concrete fact already implies the insight, do not append it.**
  "Handled 120 escalations across 9 agents, exactly the case where context gets
  lost" — cut everything after the comma.
- [ ] **No adjective whose job is to signal significance.**
- [ ] **No philosophy in a bullet.** "A policy nobody can follow does not get
  followed" belongs in an interview answer. A bullet states what was done.
- [ ] **No defence built around a known limitation.** State the honest scope
  plainly and stop.
- [ ] **The summary must not pre-prove everything.** It answers *what kind of
  professional is this, and what is unusually valuable*; the experience section
  proves it.
- [ ] **Borrowed employer vocabulary stays out of a general resume.** One
  company's product language belongs only in a copy tailored to that company.
- [ ] **The test for every bullet: is this evidence, or commentary on
  evidence?** If removing a clause loses no fact, it was commentary. This never
  licenses vagueness: every number, name and date stays.

Full method and the application-prose half:
`.claude/skills/job-application-pipeline/references/application-writing-style.md`.
