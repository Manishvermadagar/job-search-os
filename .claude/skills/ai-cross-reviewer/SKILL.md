---
name: ai-cross-reviewer
description: Use after resume-builder/resume-analyser have already produced a resume+CV draft (Mode A), or after job-application-pipeline has drafted cover-letter/application-answer content for a specific posting (Mode B), when a ChatGPT second opinion is wanted before finalizing — "get ChatGPT to review this resume", "cross-review my resume", "what would ChatGPT say about this", or job-application-pipeline's own mandatory pre-submission content check. Not a replacement for resume-analyser's code-checked gate; this is an additional, external opinion layered on top, always followed by Claude proofreading whatever comes back against career-bank.md and the JD before any of it is used.
---

# AI Cross-Reviewer

## Why this exists

A model reviewing its own drafts shares its own blind spots. This skill puts
an independent second opinion from a different model (OpenAI, via the Codex
CLI or ChatGPT) into the loop, on content that is already drafted. It does
not replace `resume-analyser`'s code-enforced checks (banned phrases,
third-person pronouns, ATS structure). Those stay, because they are
objectively checkable. This is an additional qualitative pass layered on top.

The second opinion is only useful if it cannot smuggle in new facts. Every
fix that comes back is fact-checked against `resume-data/career-bank.md`
before it touches a real file.

## Two modes

**Mode A — Resume/CV.** Reviews an already-drafted resume or CV for general
resume quality, and against the JD when the resume was tailored to one.

**Mode B — Written application content.** Reviews cover letters, cover
emails and application-answer text **with the job posting as context**, so
the feedback is calibrated to what this employer actually asked for.

Mode B **requires an application-instance identity** before it runs:

- employer and role;
- posting source as a stable identifier — the actual posting URL, not just a
  board name (a role can be reposted or listed more than once);
- channel, from the vocabulary `job-board` / `company-careers` / `email`;
- the exact source file reviewed, with a version note (a revision note or
  "unedited since <date>") so a later session can tell whether it is still
  the content that was reviewed.

The same role can have several application instances with near-identical
content. A review without this identity cannot be matched back to the right
one. **A saved Mode B review is valid only for the instance and source
version it names**; if the content or its JD changes materially, rerun it.

Both modes share the same process and the same fact-check discipline. They
differ only in the prompt and the save location.

## What the reviewer may evaluate, and what it cannot decide

The reviewer **may** evaluate the supplied writing for clarity, relevance,
positioning, ATS and readability signals, tone and seniority fit, keyword
alignment, internal consistency, redundancy against the resume, and whether
an answer actually answers the question asked. Those are substantive content
judgments, and this skill should not pretend the reviewer only polishes prose.
Believing that label too literally leads to weaker fact-checking.

The reviewer **never** decides whether a job is pursued, how a role scores
for fit, or which channels an application goes out on. A reply saying "I
wouldn't apply to this role" or "reach out to the hiring manager directly" is
inadmissible on those questions.

**Split, don't discard.** "I wouldn't apply because the resume shows no
enterprise experience" bundles an inadmissible pursuit opinion with a content
observation that may be accurate. Reject the conclusion; evaluate the content
observation on its own merits.

## Review route

### Default: OpenAI Codex CLI

1. Confirm the CLI is installed and signed in:

   ```
   codex login status
   ```

2. Write the filled prompt to a file (see Step 2 below), then run the review
   non-interactively and read-only:

   ```
   codex exec --sandbox read-only --skip-git-repo-check -C <dir> - < prompt.md > out.md
   ```

   `<dir>` is the folder holding the files the reviewer may read, usually
   `resume-data` or `resume-data/output/<slug>`. Read-only sandboxing means
   the reviewer can read files but cannot edit anything. Write `out.md`
   straight into the review folder (see "Saving rounds").

3. For a follow-up round, write a new prompt file containing only the next
   question and the current version of the file, and run the same command
   again. Each round is its own saved prompt and its own saved reply.

### Fallback: manual ChatGPT copy-paste

If `codex` is not installed or not signed in, write the prompt to a file in
the review folder and ask the user to paste it into ChatGPT and paste the
complete reply back. Save that reply verbatim the same way.

Record which route was used as the first line of every saved reply:
`Review source: codex exec` / `manual paste, template` / `manual paste,
free-form`. A codex run is captured directly and is the most reliable. A
manual paste depends on the user pasting the complete reply. **A free-form
ChatGPT conversation the user pastes in (not built from a template) is
advisory only**: it skips the safeguards in the templates (anti-fabrication
rule, separation of candidate and employer facts, read-only resume
instruction), so it does not close out a required review round on its own.
Say so rather than treating it as equivalent.

## How a review session runs

- **One question per round.** Never bundle a correctness check and a style
  check into the same prompt. The centre of gravity of a prompt decides what
  actually gets audited; a bundled prompt returns mostly style notes and
  misses the factual ones. Run correctness (facts, boundary) before style,
  because a style edit can reintroduce a factual problem.
- **The first round is unguided.** Send the file, a line on what it is for
  ("this is my resume for operations manager roles"), and "review this".
  No checklist and no framing. Every guided prompt narrows what gets
  examined. The structured templates in `references/` are for later rounds,
  once the unguided read is on record.
- **Never narrate your own edits** in a follow-up prompt. Saying what changed
  tells the reviewer what to expect instead of letting it find things. Send
  the current file and the question.
- **Fixes come back as replacement blocks, never as a whole-file rewrite.**
  A full rewrite silently drops content that was not discussed. Every prompt
  asks for:

  ```
  REPLACEMENT
  OLD:
  <exact text currently in the file>
  NEW:
  <replacement text>
  END
  ```

  and ends with exactly one of `VERDICT: READY TO SUBMIT` or
  `VERDICT: NOT READY`.
- **Loop until the verdict is READY TO SUBMIT.** Each round reviews the
  current file, after the previous round's accepted fixes are applied.

## The process — three steps, either mode

1. **Claude drafts first** through the normal pipeline. Mode A:
   `resume-builder` → `resume-content-optimizer` → `humanizer` →
   `resume-analyser`. Mode B: the application team
   (`application-question-interpreter` → `application-strategist` →
   `application-writer` → `application-verifier`), with the tailored resume
   already reviewed under Mode A. This skill never writes a first draft.

2. **Get the external read.** Round 1 is unguided (above). Later rounds use
   `references/chatgpt-prompt-template.md` (Mode A) or
   `references/chatgpt-prompt-template-application-content.md` (Mode B),
   one question per round. Run it through the Codex CLI or the manual
   fallback. **Save the complete reply verbatim before doing anything else
   with it.** If a session produced several replies (a regeneration, an
   interrupted answer), save only the one used and note that others existed.

3. **Fact-check every returned block, then apply the ones that pass.** This
   is the step that protects against fabrication: an external model asked to
   improve a resume will readily invent a plausible number. Each block runs
   through **admissibility first, then precedence, then independent
   judgment**. Do not collapse these into one "disagree, so reject" bucket.

### Admissibility — reject outright

- **Unsupported new claim.** Reject a new candidate-history claim unless it
  traces to `resume-data/career-bank.md`; silence is not permission. Reject a
  new employer or posting claim unless it traces to the verified posting or
  company source. Check each number against the source for the subject it
  describes; an employer-side number does not require a career-bank line.
- **System constraint violation.** The block asks for something a rule in
  this repo forbids: exceeding the page limit, listing a tool the career bank
  marks as no experience, a rendering change that breaks ATS constraints,
  sending something this system only drafts.
- **Outside the reviewer's authority.** A pursuit, fit or channel opinion.

### Precedence — if admissible, which of four cases applies

- **Reviewer vs. `career-bank.md` facts** → the career bank wins, always.
- **Reviewer vs. the JD** (Mode B always; Mode A when the resume is
  tailored) → the verified JD is authoritative for what is relevant. If the
  reviewer seems to have misread the ask, first check whether the prompt
  included the full JD and listing metadata. If the JD itself looks
  contradictory or stale, flag that to the user; "the JD wins" does not
  resolve a broken JD.
- **Reviewer vs. a standing repo rule** (a no-experience tool, a required
  disclosure, a page limit) → the repo rule wins. Say so explicitly in the
  round record; do not apply or reject silently. A reviewer asking for the
  same excluded item round after round is not evidence it should return —
  the reviewer cannot see why it was excluded.
- **Reviewer vs. the user's own voice** → the user decides. The voice
  baseline is the latest user-approved draft, not the most recent AI pass.
  Present both versions rather than adopting the rewrite. This matters more
  in Mode B, where application prose is more voice-sensitive than bullets.

### Independent judgment — everything else

If a block is admissible and hits none of the four cases, Claude still
decides whether it is actually correct. The reviewer can simply be wrong
(calling a bullet redundant when it is not, misjudging tone). "None of the
cases applies" is not the same as "therefore apply it."

**Source-of-truth note.** `career-bank.md` is the authority for facts about
the candidate's history. Other facts have their own authority: employer
requirements → the JD; field limits and mechanics → the application page;
already-approved wording → the existing source file; project policy →
`CLAUDE.md` and the skills. Do not reject an employer-side fact for not
appearing in the career bank.

**Scores are diagnostic labels, not measurements.** If a score and its own
narrative disagree, act on the narrative. A score never becomes a pass/fail
threshold on its own.

### Applying accepted blocks

- Apply an accepted block **exactly as written**: find the OLD text in the
  source file and replace it with NEW. If OLD does not match the file
  exactly, do not guess where it was meant to go — record the block as
  unapplied and ask for it again in the next round.
- Record every rejected block in the round record with the reason
  (unsupported claim, constraint, authority, precedence case, or judgment).
- Mode A: re-run `resume-analyser/scripts/analyze_resume.py` afterwards to
  confirm nothing regressed, and check the result against
  `resume-content-optimizer/references/positioning-and-prioritization.md`.
- Mode B: re-run `humanizer` over every changed passage. A fix that reads
  well can reintroduce AI-writing tells. Then run `application-verifier` on
  the complete final text again; only its PASS on that version clears the
  content for the user's review.

## Saving rounds

Every round is saved under `resume-data/output/<slug>/review/`:

- `round-N-prompt.md` — the exact prompt sent;
- `round-N-reply.md` — the verbatim reply, headed by the review-source line
  (and, in Mode B, the application-instance identity);
- `round-N-decisions.md` — each block: applied, rejected (with reason), or
  unapplied (OLD did not match).

The folder is the record of what was asked, what came back and what was
done with it. Never edit a saved reply.

## Render and submit gate

**Mode A:** no PDF/DOCX render until the review rounds the user wants are
done and applied. If the user says to render early, that waiver covers the
render only.

**Mode B:** draft the application text, including any cover email, before
external review. If external review is requested, complete it or obtain the
user's waiver before filling the form with that text or presenting the email
as final.

**Nothing in this skill submits or sends anything.** The final application
is shown to the user, and the user submits it.

## Log genuinely new lessons

If the reviewer flags something `resume-analyser/references/qa-checklist.md`
or `positioning-and-prioritization.md` does not yet check for, and it is a
real recurring issue, add it to those files and log the originating mistake
in `resume-data/resume-qa-ledger.md`. **One reviewer opinion alone is not
enough to promote a standing rule**: it needs a second independent instance
or the user's explicit agreement. Say which applies when logging it. Each
review should make the next Claude-only draft better, not just fix one file.

## Guardrails

- Never send the reviewer content that is not already in the user's own
  drafted material and supporting files. No new content enters through this
  skill in either direction.
- The review is an opinion, not ground truth. Check every block for
  admissibility before precedence is even considered.
- **The reviewer does not decide** pursuit, fit or channels. That is
  enforced by treating such recommendations as inadmissible, not by relying
  on the reviewer's restraint.
- Never ask for a whole-file rewrite. Section-level replacement blocks only.
- Never submit, send or post anything. Prepare and show the user.
