# Application writing style — the human-lens rules

Most weak applications fail on **what is being said** and on **applicant
psychology**, not on accuracy or tone. A review loop that checks only facts and
AI-sounding phrasing will pass text that is honest, correct and unsendable.

> A humanizer cannot fix writing whose argument is wrong.

That is the governing sentence. Tone is the last 10%. These rules are the
other 90%, and they are applied **at drafting time**, before any humanizer or
reviewer round.

---

# PART ONE — THE METHOD

**Read this before the rules. The rules are checks on the output; this is how the
output gets made.**

## The root cause, stated mechanically

An AI answers a question by **retrieving relevant facts about the candidate**.
Human persuasive writing starts by **deciding what the reader needs to believe**.
Those are different operations, and the first one silently rewrites the question.

Given "What interests you about working for this company?", the model activates
`job → qualifications → match experiences → demonstrate fit` and answers a
different question: *"Explain why this candidate is relevant to this role."*
**That transformation is the bug.** The company becomes the trigger and the
candidate the subject. It should be the reverse.

The correct operation:
`question → identify the reader's decision → formulate the genuine answer →
select only the evidence needed to make it believable.`

## Why it volunteers weaknesses: symmetrical truth-telling

A second structural bug. Models are pulled toward completeness, balance and
qualification, so on noticing a mismatch they "responsibly" disclose it. Honesty
is not the problem; **answering a question the employer did not ask** is.

> A good application is not a complete representation of the candidate. It is a
> **truthful selection** from the complete representation of the candidate.

Omission can feel like deception to a model. It is not. Hiring communication runs
on relevance.

## Two passes. Never one.

The failure mode is an integrated `read JD + read resume + generate` step, which
invites automatic matching. Split it.

### PASS 1 — THINKING. No prose allowed.

Fill these seven fields before writing a sentence:

1. **Literal question** — what exactly was asked?
2. **Hidden decision** — what is the employer trying to learn by asking it?
3. **One-sentence answer** — what should the reader believe after reading this?
4. **Company-specific observation** — what is distinctive here?
5. **Candidate-specific connection** — why does that observation matter to *this*
   person?
6. **Evidence** — which 1–3 real facts make that connection credible?
7. **Exclusions** — which true facts are tempting but irrelevant? **Write them
   down explicitly** (for example, a metric the candidate lacks or a schedule
   they have not worked). This field prevents most volunteered weaknesses.

### PASS 2 — WRITING.

Sentence 1: answer the question directly. Sentences 2–3: the specific reason.
Sentences 4–5: personal evidence, only to make that reason credible. **Then stop.**

## The forcing function: write the answer without mentioning the candidate

For any "why us" question, first write 2–4 sentences containing **only** the
company, product, problem, market, direction. No "I". No resume. No
qualifications. Answer: *what is interesting about this company even if the candidate were
not applying?*

Only then ask why this person cares. **Direction of causality matters:**

- Wrong: *I did X, built Y, handled Z, therefore I am interested in you.*
- Right: *This is interesting because it solves X. I care about X because I have
  personally paid the cost of solving it manually.*

## One primary reason. At most one secondary. Cut the rest.

A candidate with real range generates many valid matches, and abundance is the
trap — AI includes every match because each looks like evidence. Humans remember
a coherent point, not an inventory.

## The evidence test

For every supporting fact: **if I delete this sentence, does the answer become
less believable — or merely less impressive?** If merely less impressive, cut it.

## Friction is what makes it memorable

Competence is free now; hundreds of applicants have it. What is not substitutable
is evidence that carries **cost**: responsibility, consequences, failure, a hard
tradeoff, something built because nothing existed. Look in `career-bank.md` for material
like this — for instance, writing the first training guide because none existed,
or handling a high-stakes escalation. Polished prose sands the friction off.
Leave it on.

## Pick one identity per application, not all of them

Most candidates have several true, distinctive framings (for example: "the person
who builds structure where none exists", "the manager who turned individual
judgment into training and QA", "the operator who moves from frontline detail to
system design"). Choose the one that answers *this* question rather than
establishing all of them every time. Any of them beats "5 years of experience in
X". Record the framings in the user's profile files.

## The five pre-submission tests

1. **Subject test.** Circle the subject of each sentence. If it is I / I / I / I
   on a question about the company, the centre of gravity is wrong.
2. **Deletion test.** Remove every sentence referring to the candidate. Does
   anything remain that answers the literal question? If it empties out, this was
   a qualifications pitch disguised as an answer.
3. **Swap test.** Replace the company name with another company. **If 80% still
   works, it is generic.** A real "why this company" answer breaks when
   transferred.
4. **Resume duplication test.** Could the hiring manager already learn this from
   the resume? If yes, do not repeat it unless it serves a new argument.
5. **Voluntary damage test.** Did I introduce any fact that makes the candidate
   look less suitable when the question did not require it? Remove it — unless
   omission would make another claim misleading, or the form asks directly.

## The permanent shift

> Stop treating an application as a resume converted into prose.
> The resume is the evidence inventory. The application is an argument.
> The question determines the argument. The company determines the relevance.
> The candidate's history supplies selected proof.

Replacing "leverage" and "robust" with casual words on top of a wrong argument
just produces casual AI writing. **The argument has to be right first.**

---

# PART TWO — THE RULES (checks on the output)

---

## Rule 1 — Answer the question that was actually asked

A common failure: asked **"What interests you about working for this company?"**,
the draft is mostly "here is what I have done" and contains **no fact about the
company**. It answers "why am I good" — a different question nobody asked.

- A "why us" question is about **them**. The centre of gravity must be the
  company: their problem, their product, their customers, their stated values.
- The candidate's evidence is there to **prove the interest is informed**, not
  to be the subject.
- Rough split for a "why us" answer: **more than half the words on them**, with
  the candidate's experience entering as the reason the candidate recognises their problem.
- Use the **Three Whys**: why this company, why this role, why me — in that
  order. Most drafts jump straight to "why me" because that is the material
  closest to hand.

**Test:** delete every sentence that mentions the company. If what remains is
still a complete answer, the answer never addressed the question.

## Rule 2 — Never volunteer a deficit

No human applicant opens by listing what they do not have. Closing on paragraphs
of unprompted disclosure (a missing metric, a schedule never worked) is not honesty, it is self-prosecution in a document
whose entire job is persuasion.

**The distinction that matters, and it is not subtle:**

| | |
|---|---|
| **Honesty** | Never claiming what the candidate has not done. Answering truthfully when asked. **Unchanged, absolute, non-negotiable.** |
| **Self-prosecution** | Raising a gap nobody asked about, in a persuasive document, where silence was available and truthful. **A defect.** |

**Disclose a gap only when one of these is true:**
1. A form or person **directly asks** (a literal question about years, a tool, a
   shift, a salary).
2. It is **visibly obvious** in the resume and will raise the question anyway,
   so leaving it unaddressed is worse than addressing it.
3. A **hard rule** requires a truthful literal answer (a direct question about a tool
   the candidate has never used, for instance).

**Otherwise: say nothing about it.** Silence is not a lie. Leaving out the
weakest thing about a candidacy is what every honest applicant does.

### Rule 2A — Omission does not permit implication

**The loophole Rule 2 opens if applied mechanically, closed.** You may omit a
weakness nobody asked about. You may **not** then write positive language that
causes a reasonable reader to infer the experience the candidate lacks.

When a positive claim would create that inference, **narrow or cut the claim** —
do not bolt on a disclaimer paragraph to make an overreaching sentence safe.
The disclaimer is not the fix; the accurate phrasing is.

The sharper statement of the boundary: *do not introduce a negative comparison
unless omitting it would make a positive statement misleading, evasive, or
obviously incomplete.*

Three places omission stops being clean:

1. **The sentence creates a false inference.** "Extensive experience managing
   overseas accounts during their business hours" is not fixed by omitting "I have
   never worked that shift" — the positive sentence is the problem. Narrow it.
2. **The omission leaves an obvious contradiction.** The threshold is not "a
   recruiter could notice" — every candidate has visible gaps. It is: *would a
   reasonable reader hit a statement in this document that reads inconsistent or
   incomplete unless the limitation is explained?* Usually the answer is still
   accurate phrasing, not a confession.
3. **A direct question is asked.** Silence is evasive. The limitation belongs in
   the answer. This is the cleanest case and it is unchanged.

**This is not licence to overclaim.** The correct move is *omission*, never
spin. Any gaps section in `career-bank.md` still governs what to say **when
asked**.

## Rule 3 — Specificity is the actual anti-AI signal

Recruiters do not run detectors. They pattern-match against thousands of
AI-written applications a week, and **generic content is the rejection trigger, not
AI use**. Properly specific writing is not flagged even when AI helped
produce it.

So the defence is not vocabulary laundering. It is **detail only this candidate,
applying to this company, could possibly have written.**

- Name something real about the company: a phrase from their own site, a named
  customer, a use case, a competitor, a value from their culture page, a number
  from their case study.
- Pair it with something real from the candidate's life that is not on the resume in the
  same words.
- **Do not parrot the JD back.** The hiring manager wrote it. Restating the
  responsibilities proves nothing.

**The "only they could have sent this" test:** if another candidate with a
different history could send the sentence unchanged, cut it.

## Rule 4 — Burstiness: vary sentence length hard

The single most reliable structural signature of AI text is **uniform sentence
length** — LLMs settle into a metronomic 18–24 words and stay there. Human
writing clusters irregularly: a long, dense, subordinate-clause-heavy sentence,
then a short one. Then off again.

- Deliberately include sentences under 8 words.
- Let one sentence run long if the thought is genuinely long.
- Check a draft by counting words per sentence. If every sentence lands in the
  high teens to low twenties, it reads as machine-made regardless of vocabulary.
- **Em dashes are a symptom, not the disease.** Cutting them while leaving
  uniform rhythm fixes nothing.

## Rule 5 — Banned openers and flagged vocabulary

Instant-tell openings, never to be used:
- "I am writing to express my (strong) interest in the [role] at [company]"
- "I am excited to apply for..."
- "proven track record", "detail-oriented professional", "results-driven"

Vocabulary flagged as statistically AI-overused (Stanford and 2026 recruiter
commentary): **delve, leverage(d), robust, pivotal, intricate, showcasing, realm,
spearheaded, synergy, tapestry, testament, underscore, seamless, landscape,
navigate, foster, meticulous, myriad, crucial, vital.**

Treat this list as a supplement to any banned-word check the resume analyser
runs.

## Rule 6 — No meta-commentary about the writing itself

Cut anything that narrates the candidate's own honesty, structure, or intent.
Examples:

- "I would rather say that now than in the second interview."
- "Two gaps worth naming rather than leaving you to find them."
- "Short version of why I'm writing."

A person managing the reader's evaluation process is the most artificial thing
a letter can do. State the thing or do not; never announce that you are about
to state it.

## Rule 7 — Warm, conversational, to a respected near-stranger

The target register: **how you would write to a colleague you like but do not
know well.** Not stiff, not formal, not a resume rendered in prose. Personality
is allowed. The list-y passive voice applicants fall into is the thing to avoid.

## Rule 8 — Lead with the strongest concrete thing

Open on something that could only be the candidate, that a reader would want to keep
reading after. Never on throat-clearing, never on the application's own
existence, never on a summary of the letter to follow.

## Rule 9 — Endings matter disproportionately

Readers remember the first thing, the last thing, and anything emotionally
distinctive. Ending on a self-introduced objection leaves the reader holding the
weakest evidence in the document.

**Never end on an objection you raised yourself.** End on the strongest truthful
reason for the reader to continue the conversation.

## Rule 10 — The curiosity test

Leading with the strongest concrete thing is not sufficient. After the first two
sentences, is there a reason to read the next two? A good opening produces one
of: *I hadn't thought of it that way* / *this person understands our problem* /
*that is unusually specific* / *I want to see where this goes.*

## Rule 11 — Every sentence needs a job

Distinct from cutting filler. A sentence can be grammatical, true and relevant
and still have no job. The legitimate jobs: establish company knowledge,
establish a genuine overlap, prove a claim, add memorable specificity, handle a
necessary logistical detail, create a transition, ask for the next step.

If a sentence does none of those, cut it. "Demonstrate honesty" is not a job.

## Rule 12 — Relevance beats comprehensiveness

An optimisation loop reaches for the largest metric and the broadest
responsibility. Strong applicants do the opposite: they pick the **one story
that makes the company's problem feel personally familiar**. One connected story
beats five disconnected qualifications.

## Rule 13 — Make the inference once

Company observation → lived overlap → implication. Then stop. Do not explain the
same connection three times, and do not compress it into a slogan instead of
stating the actual overlap.

## Rule 14 — Company research must survive disagreement

**Test: could someone inside the company reasonably say "that isn't how we think
about our product"?** If yes, the language is too categorical.

Example: *"That is your product, done by hand, on a spreadsheet"* claims
identity between a manual process and a company's whole product, which likely
does far more. The insight may be good; the equivalence is fragile. Better:
*"I was doing a version of that manually, on a spreadsheet."*

Assume the reader understands their product better than the applicant does.
Describe the overlap; never hand them a redefinition of their business to
disagree with.

---

## The drafting sequence (use this order)

1. **Research the company for 20–30 minutes before writing a word.** Their site
   — About, the specific solution/use-case page matching the role, case
   studies, careers/culture page, competitor comparison pages. Capture their own
   language for the problem they solve.
2. **Find the genuine overlap** between what they say the problem is and what the candidate
   has actually lived. It must be real; a manufactured overlap reads worse than
   none.
3. **Write the "why them" first**, before touching the candidate's experience.
4. **Add the candidate's evidence as proof the interest is informed**, not as the subject.
5. **Cut every unprompted deficit.** Check Rule 2's three exceptions honestly.
6. **Run the tests:** company-deletion test (Rule 1), only-they-could-send-this
   test (Rule 3), sentence-length count (Rule 4), meta-commentary sweep
   (Rule 6), ending check (Rule 9 — does it close on an objection the candidate raised?),
   every-sentence-has-a-job pass (Rule 11), and the survives-disagreement test
   (Rule 14).
7. **Only then** send it for review and the humanizer pass.

## What the review loop must now be asked for

A review that checks only accuracy and tone can approve text with all of the
defects above. Every application-content review should also ask, explicitly:

- Does this answer the question that was actually asked, or a different one?
- Does it contain any fact about the company? Name them.
- Does it volunteer any weakness nobody asked about? Quote it.
- Would a hiring manager reading 200 of these remember this one? Why?
- Count the sentences. What is the word-count spread?

Accuracy review alone will pass writing that is honest, correct, and unsendable.

---

## Sources

- Ask a Manager, on conversational register and not writing a resume in prose:
  https://www.askamanager.org/2024/11/this-is-how-to-write-a-good-cover-letter.html
- Recruiter AI-detection patterns, 2026:
  https://hirelytica.com/blog/ai-cv-red-flags-recruiter-detection-2026
  https://www.wasitaigenerated.com/research/ai-detection-hiring-recruitment
- Burstiness / sentence-length variance as the primary structural tell:
  https://www.textsight.ai/blog/sentence-length-variance/
  https://www.duey.ai/post/em-dash-ai-writing
- "Why do you want to work here" — the Three Whys and research depth:
  https://resources.biginterview.com/interview-questions-answers/why-do-you-want-to-work-here/
  https://novoresume.com/career-blog/why-do-you-want-to-work-here
- Do not volunteer weaknesses in a cover letter:
  https://www.businessnewsdaily.com/6879-cover-letter-mistakes.html
  https://www.indeed.com/career-advice/resumes-cover-letters/what-not-to-put-in-a-cover-letter
- Do not parrot the job description; tell the story instead:
  https://resume.io/cover-letter-examples/customer-success

---

# PART THREE — RESUME WRITING (a different disease)

The resume is not a cover letter in bullets, and its AI failure mode is
different. The facts were never the problem. **Argument density** is.

## The core rule: when a fact already implies the insight, do not append it

> AI explains. Good resume writing lets the hiring manager conclude.

Stating the action, the context where necessary, and the result — then stopping —
creates **reader participation**. The manager supplies the interpretation and
therefore believes it. The moment the resume explains why the achievement was
impressive, the candidate is doing the reader's job, and trust drops.

"Found 1,200 of 4,000 invoiced records were duplicates" makes a reader think
*that is a serious audit.* Adding a clause about how rigorous it was takes that
thought away from them.

## What AI resume writing does, and what to do instead

| AI tendency | Human practice |
|---|---|
| Explains why each achievement matters | States action, context, result. Stops. |
| Adjectives that assign significance | Concrete responsibility; let scale speak |
| Achievement + interpretation + implication in one bullet | One bullet, one fact |
| Anticipates and pre-empts objections | Answers them if asked, not before |
| Compresses many accomplishments into one line | One per line |
| Turns every fact into a competency claim | Leaves facts as facts |
| Optimises for keyword coverage | Optimises for being believed |

## Common instances of the disease

These generalise to most resumes:

1. **A summary that over-constructs identity.** Five stacked claims — leader,
   growth arc, several "firsts", a methodology label, a build — read as someone
   ensuring no accomplishment is missed. A summary should answer *what kind of
   professional is this, and what is unusually valuable about them*, then let the
   experience prove it.
2. **Adjectives that assign significance** ("highest-accountability accounts").
   The concrete fact (one mishandled issue reaches a partner's own customers) is
   more persuasive than the label.
3. **Vocabulary borrowed from one employer's product.** Acceptable only in a
   resume tailored to that employer; otherwise say what was done.
4. **Evidence followed by explanation.** "Reviewed 100 cases handled by 12
   different people — exactly why shared case history matters." The first half is
   evidence; cut the second.
5. **Aphorisms in bullets** ("A policy nobody can follow is a policy nobody
   follows"). Good in an interview, wasted space in a bullet.
6. **Defending a limitation unprompted.** State the honest scope; do not build an
   argument around it.

## The resume test

For every bullet: **is this evidence, or is it commentary on evidence?**
Keep the evidence. Cut the commentary. If removing a clause loses no fact, it was
commentary.

**This does not license vagueness.** Every number, name and date stays. The rule
removes *interpretation*, never *specificity* — they are opposites, and the
strongest resumes are dense with the second and free of the first.
