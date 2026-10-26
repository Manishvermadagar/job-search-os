# Review prompt template — Mode B (written application content)

For cover letters, cover emails and application-answer text for one specific
posting, reviewed **with the JD as context**. The reviewer may judge
relevance, evidence specificity and tone; it does not decide whether to
pursue the job or which channels to use.

Used for rounds after the first, unguided round. Run it through the Codex CLI
by default:

```
codex login status
codex exec --sandbox read-only --skip-git-repo-check -C resume-data/output/<slug> - < review/round-N-prompt.md > review/round-N-reply.md
```

If `codex` is unavailable, give the prompt file to the user to paste into
ChatGPT and save the reply they paste back.

## Identity block (saved with the reply, not sent)

The same role can produce several application instances (job board, company
careers page, email) with near-identical content. A review not tied to one
instance cannot be matched back to it later. Head the saved reply with:

```
Review source: {codex exec | manual paste, template}
Employer: {COMPANY_NAME}
Role: {ROLE_TITLE}
Posting source (URL, not a board name): {POSTING_URL}
Channel (job-board / company-careers / email): {CHANNEL}
Source file reviewed: {SOURCE_FILE_PATH}
Source version: {VERSION_NOTE}
```

A saved review is valid only for that instance and version. If the content or
its JD changes materially, rerun it.

## One question per round

Ask one per round, in this order — correctness before style:

1. **Facts** — does any candidate claim go beyond what my own text supports?
2. **Question fit** — does each answer answer the question actually asked?
3. **Evidence** — concrete example or number, or a vague claim?
4. **Tone and seniority fit** for this employer.
5. **Redundancy and length** — repeats of the resume; stated limits.
6. **Verdict** — is this ready to send?

## Order inside the prompt

Put the JD before the answers, so the reviewer reads the content as responses
to a specific ask. Pair each question with its answer directly beneath it.

## Prompt

```
I'm reviewing application content for one job before it is submitted. It is
prepared but not sent. Role: {ROLE_TITLE} at {COMPANY_NAME}
({COMPANY_STAGE_OR_SIZE}).

This round has one question:

{QUESTION}

Answer only this question.

Rules, apply before anything else. Two separate fact namespaces:
- CANDIDATE claims (my experience, numbers, tools) may ONLY come from my own
  answers, cover letter or resume below, never from the job posting. Do NOT
  introduce any candidate fact, metric, tool or example that is not already
  in my text. If an answer needs a missing detail, ask me for it.
- EMPLOYER claims may come from the posting, but never become a claim about
  me. "We serve 10,000 customers" does not mean I have enterprise-scale
  experience unless my text already says so.
- Preserve my voice where it already works. This is a personal application.
- Respect any word or character limit stated in a question.
- Do NOT rewrite whole answers or the whole letter. Return every fix as:

  REPLACEMENT
  OLD:
  <exact text currently in my draft, copied character for character>
  NEW:
  <replacement text>
  END

Output as plain markdown, in order:
## Findings
## Replacements
## Questions for me (if any)
## Resume contradictions or redundancy (if any)
End with exactly one line: VERDICT: READY TO SUBMIT or VERDICT: NOT READY

---

## JOB POSTING (verbatim, legal boilerplate stripped)

{JD_TEXT}

Comp band: {COMP_BAND}
Experience expected: {EXPERIENCE_REQUIRED}
Application mechanics: {APPLY_MECHANICS}

---

## APPLICATION QUESTIONS AND MY DRAFTED ANSWERS

{QUESTION_1}
Stated limit (if any): {LIMIT_1}
My answer: {ANSWER_1}

{QUESTION_2}
Stated limit (if any): {LIMIT_2}
My answer: {ANSWER_2}

[... repeat per question ...]

---

## COVER LETTER / COVER EMAIL

Subject (if email): {SUBJECT_LINE}
Delivery: {INLINE_BODY_OR_ATTACHMENT}

{COVER_LETTER_CONTENT}

---

## MY RESUME (already reviewed and locked: do NOT rewrite or score it. Use it
## only to flag contradictions or redundancy with the content above.)

{RESUME_CONTENT}
```

## After the reply comes back

1. Save it verbatim, headed by the identity block, to
   `resume-data/output/<slug>/review/round-N-reply.md`.
2. Fact-check each REPLACEMENT block per `ai-cross-reviewer/SKILL.md`:
   admissibility (reject unsupported claims, constraint violations and
   pursuit/fit/channel opinions), then precedence (career-bank facts win, the
   JD wins on relevance unless it looks broken, standing repo rules win, the
   user's latest approved wording wins over a suggested rewrite), then
   independent judgment for the rest.
3. Apply accepted blocks exactly, record every decision in
   `review/round-N-decisions.md`, and re-run `humanizer` over changed text.
4. Loop until VERDICT: READY TO SUBMIT.

Draft any cover email before this review so the reviewer can inspect it. If
external review is requested, complete it or obtain the user's waiver before
filling the form with reviewed text or presenting the email as final. Nothing
is submitted or sent by this skill; the user does that.
