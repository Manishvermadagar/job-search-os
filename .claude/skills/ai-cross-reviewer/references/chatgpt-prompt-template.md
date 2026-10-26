# Review prompt template — Mode A (resume / CV)

Used for review rounds **after** the first, unguided round (see
`ai-cross-reviewer/SKILL.md`, "How a review session runs"). Run it through
the Codex CLI by default:

```
codex login status
codex exec --sandbox read-only --skip-git-repo-check -C resume-data/output/<slug> - < review/round-N-prompt.md > review/round-N-reply.md
```

If `codex` is unavailable, give the same prompt file to the user to paste into
ChatGPT and save the reply they paste back.

## One question per round

Each round asks **one** of the questions below, not all of them. Order:

1. **Facts** — does any statement claim more than the source supports?
2. **Positioning** — what single role would a skimming recruiter assume this
   person is applying for? Which sections blur that?
3. **ATS and structure** — section headers, keyword alignment to the JD,
   parseability.
4. **Achievements** — bullets stating a responsibility without an outcome.
5. **Language** — redundancy, weak verbs, tense, padding, length.
6. **Verdict** — is this ready to send?

Correctness (1) always runs before style (3-5), because a style edit can
reintroduce a factual problem.

## Filling the placeholders

- `{EMPLOYER_TYPE}` — the actual target, e.g. "an early-stage startup",
  "a Series B company", "a large process-driven enterprise". The wrong
  assumption miscalibrates the tone review.
- `{JD_TEXT}` — include it when the resume was tailored to a posting (the
  normal case inside the application pipeline), from that folder's
  `jd-posting.txt`. Omit the section only for an untailored base resume.
- `{QUESTION}` — one question from the list above.
- `{RESUME_CONTENT}` / `{CV_CONTENT}` — the current file, in full.

**Scope note.** "The source text" in the prompt means only what is in this
prompt, not the whole career bank. That stops the reviewer treating anything
true somewhere as fair game for this document. If a relevant career-bank fact
is missing, that is a prompt-construction gap to fix, not something the
reviewer should fill.

## Prompt

```
Review the resume below. This round has one question:

{QUESTION}

The resume is for {EMPLOYER_TYPE}. Answer only this question; do not review
anything else in this round.

Rules, apply before anything else:
- Do NOT introduce any employer, title, date, metric, tool or example that
  is not EXPLICITLY stated in the source text below. A plausible inference
  is still an invention: "managed strategic accounts" does not license
  "worked with enterprise customers". If a bullet would be stronger with a
  detail that is missing, ask for it as a question; never invent it.
- Do NOT rewrite the whole document. Return every fix as a block:

  REPLACEMENT
  OLD:
  <exact text currently in the resume, copied character for character>
  NEW:
  <replacement text>
  END

- Keep each fix to the smallest section that solves the problem.
- Any score you give is a label; explain it in one line tied to the text.

Output as plain markdown, in order:
## Findings
## Replacements
## Questions for the candidate (details you would need, if any)
## Verdict
End with exactly one line: VERDICT: READY TO SUBMIT or VERDICT: NOT READY

---

## JOB POSTING THIS RESUME WAS TAILORED TO
## (omit this section for an untailored resume)

{JD_TEXT}

---

## RESUME CONTENT

{RESUME_CONTENT}

---

## CV CONTENT (omit if not reviewing a CV)

{CV_CONTENT}
```

## After the reply comes back

1. Save it verbatim to `resume-data/output/<slug>/review/round-N-reply.md`,
   with the `Review source:` line at the top, before doing anything else.
2. Fact-check each REPLACEMENT block against `resume-data/career-bank.md`
   using the admissibility → precedence → judgment sequence in
   `ai-cross-reviewer/SKILL.md`. Reject any block whose NEW text carries a
   fact the career bank does not contain.
3. Apply accepted blocks exactly; record every decision in
   `review/round-N-decisions.md`.
4. Re-run `resume-analyser/scripts/analyze_resume.py`, then run the next
   round until the verdict is READY TO SUBMIT.
