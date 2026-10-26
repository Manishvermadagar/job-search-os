# Positioning and prioritization

Structural problems that no code check catches: what the resume is *about*,
what leads, and what gets cut. This is a **standard step in every resume
build**: run through it during drafting (`resume-content-optimizer`) and again
during proofreading (`resume-analyser`, `resume-builder`). It is cheap to check
and expensive to discover after the resume has been sent.

## 1. One primary identity, not two co-equal ones

If the candidate's experience spans two domains (e.g. Operations and Customer
Success), the summary picks **one as the category and frames the other as the
domain that expertise was built in**. Use **"[Primary category] leader with
deep [secondary domain] experience"**, not "[Primary] and [secondary]
[role]." Two co-equal categories read as uncertainty about which job the
candidate wants.

Decide the primary category by asking which one the *differentiating*
achievement (#4) belongs to.

## 2. Run the "skimming recruiter" test explicitly

Ask: "reading top to bottom in under 30 seconds, what single job title would a
recruiter assume this person is applying for?" If two or more plausible answers
exist, positioning isn't done.

## 3. Internal-authority details don't sell externally; prioritize scope and impact

A bullet describing authority held ("including performance decisions up to
termination") is true but shows nothing a recruiter weighs: scale, ownership
breadth, or outcome. Cut it to a clause inside a broader bullet, or show the
authority through its use ("Hired and onboarded 12 agents end to end"
demonstrates hiring authority better than stating it).

## 4. Elevate the single most differentiated achievement

Every candidate has one achievement that is rare relative to their job title
(e.g. a support lead who built the team's reporting system themselves). That
achievement:
- Appears in the summary's second sentence, not only later.
- Gets enough bullets in the **resume itself** (3-4 concrete ones) to prove the
  claim. A summary claiming "built X" backed by one thin bullet under-proves it,
  whatever the CV holds (#7).
- Is described in terms the target category cares about, not the literal
  technology (#5).

## 5. Frame niche technical work by the business capability it shows

If an achievement lives in a niche adjacent to the target role (e.g. a
marketing-data audit on an Operations resume), title it by the capability it
demonstrates: vendor auditing, risk detection, data validation,
cross-functional remediation, executive reporting. The niche detail stays in
the bullets underneath.

## 6. Check for missing business-impact metrics: ask, don't omit or invent

Operational metrics (CSAT, response time, team size, hiring volume) prove
execution but read as function-level signals. Business-impact metrics
(retention, churn, revenue, SLA compliance, cost avoided, productivity per
person) read as manager-level signals. Check `career-bank.md` for them; if none
exist for an achievement that plausibly had one, **ask the candidate for the
real number**. Never invent a figure.

## 7. The resume's claims must not outrun its own proof

The CV may hold more depth, but every claim in the resume summary needs
supporting bullets in the resume itself. When trimming from CV to resume,
protect the differentiator's proof bullets first.

## 8. Avoid the "proof dump"

Including every real fact with equal weight (a one-off training session next to
a system launch) signals that nothing is prioritized. Organize content around
3-4 pillars that map to the identity from #1, for example: Operations
Leadership, Process & Systems, Client Operations, Analytical Execution. Real but
tangential items go to the CV only, once the resume proves each pillar.

**The CV is not a dumping ground either.** If a single role climbs past ~10-12
bullets even in the CV, re-check each against the locked pillars (#11). A real
accomplishment that maps to no pillar is a candidate for deletion, not just
demotion.

## 9. Mandatory honesty disclosures: keep the disclosure, fix apologetic tone

If `career-bank.md` requires a disclosure (e.g. "directed AI-assisted
development rather than writing the code personally"), reviewers may flag
apologetic phrasing ("with no engineering background", repeated) as weak. The
fix is **not** dropping the disclosure. Use the bank's neutral phrasing, e.g.
"directed AI-assisted development, reviewing and testing everything that
shipped."

**Check the Skills section in the same pass.** Prose and skills lists are
written separately, so a bullet can apologize for depth that the skills line
silently overclaims ("Python, Flask, SQL" listed flat). Qualify the stack
("Python (basic), SQL (basic)") whenever a technical-depth disclosure is tuned.

## 10. When a self-built tool shows initiative, not a technical credential, subordinate its stack

Leading with a framework list frames a project as an engineering credential.
That suits a technical profile but not, say, a Customer Success profile, where
the same project is evidence of "saw a visibility gap and closed it." Check
which framing the profile wants; when the tool isn't the point, name the stack
briefly after the impact.

## 11. Lock an ordered list of positioning elements before drafting

A funnel like **Identity → Industry → Scale → Segment → [ranked
differentiators] → Leadership** turns "does this bullet belong" into a
checkable question. Everything else should visibly support that story, not
compete as a separate identity. Write the list explicitly (in the profile file
or at the start of drafting) before writing bullets.

## 12. Disclose an honest gap once, late, and paired with the foundation

When a JD lists several responsibilities the candidate hasn't done, naming each
as it comes up makes the aggregate read as an argument against the application.
The no-fabrication rule governs **whether** a gap is disclosed, not **how many
times**. Budget **one sentence, in the closing third, naming the gaps and the
transferable foundation together**: "I have not worked directly in X, Y or Z;
I would bring a foundation in A, B and C and a record of reaching ownership in
unfamiliar domains quickly." Then stop.

## 13. Career-bank phrasing is internal shorthand: observation vs. conclusion

`career-bank.md` may record conclusions (legal, causal, evaluative) that are
fine internally and unsafe to send. Before any bank phrase ships, ask whether it
states an **observation** or a **conclusion**. Ship the observation: "2,400
billed items, 1,500 unique, a 38% duplicate rate" is more convincing than
"vendor fraud," and defensible under questioning. Words to catch: fraud,
negligence, incompetence, lied, stole, deliberately: anything asserting intent
or wrongdoing rather than describing evidence.
