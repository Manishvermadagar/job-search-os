---
name: resume-visual-format
description: Use when a resume's content is already correct but it reads as a wall of equally-weighted text — "make my resume look better", "fix the formatting", "it looks flat", "the recruiter can't see my achievements", or when rendering any resume to PDF/DOCX. Defines the visual-hierarchy design system (typography, section architecture, metric bolding, page-break rules) that pdf-report's resume mode and resume-docx-export both implement. This is a formatting skill — it never changes claims, metrics or wording; for content work use resume-content-optimizer.
---

# Resume Visual Format

> **Status: settled.** Arial default, 2-page auto-fit, and the section
> architecture and emphasis budget below are fixed. Treat this as the spec to
> *implement*, not to re-open; further redesign passes tend to make it worse.
> Changes should be per-profile content work (`resume-content-optimizer`), not
> layout.

## The problem this exists to solve

A resume can have real ownership, real scale and real measurable impact and
still fail, because the formatting makes the reader **extract the story
themselves**. When every bullet carries the same visual weight, a recruiter
has to read all of it to find any of it — and they will not.

**Visual weight is a claim about relative importance.** A resume where a
routine process bullet and a 30%-overbilling vendor audit render
identically is misinforming the reader about what matters. Flat formatting is
an accuracy problem, not only an aesthetic one.

## The four reading layers (the governing principle)

Optimise for all four. **Never sacrifice layer 4 to improve layers 1–3.**

| Layer | Time | What the reader must get |
| --- | --- | --- |
| 1 | 3 sec | Role, scale, progression — *e.g. operations leader · 200K users · 18-person team · 3 functions · promoted once* |
| 2 | 10 sec | The measurable outcomes — CSAT ↑, response time ↓, systems built |
| 3 | 30 sec | The methodology behind those results |
| 4 | full read | What was identified → what changed → how it shipped → what happened |

This is why bullets **do not get shortened**. Cutting
"Audited a vendor's 14 months of invoices against delivery logs…" down to
"Audited vendor invoices and found 30% overbilling" is more scannable
and strictly worse as evidence — it deletes initiative, investigation, scale,
risk and remediation. **Keep the substance; use typography to surface the
result.** Don't optimise the resume into a pile of disconnected metrics.

## The rule: hierarchy, not graphics

Use **size → weight → spacing → alignment → one restrained accent**.

**Never add:** skill bars, star/percentage ratings, progress rings, charts,
icons replacing words, profile photos, two-column sidebars, decorative
timelines, large colored blocks, Canva-style templates. Several break ATS
parsing outright; all read as less professional, not more.

Two-column is specifically wrong here despite looking designed: with
substantial experience + quantified achievements + projects + skills +
education, a single column with good hierarchy is both more readable and more
parseable.

Target mix: **80% professional corporate, 15% modern SaaS/operations, 5%
personality.**

## Typography spec

Implemented in `pdf-report/scripts/resume_to_pdf.py` and mirrored in
`resume-docx-export/scripts/resume_to_docx.py`. **Change a token in one and
you must change it in the other.**

| Element | Size | Weight | Color |
| --- | --- | --- | --- |
| Name | 24 pt | bold | accent |
| Contact line | 9.3 pt | regular | muted |
| Section heading (uppercase) | 12.5 pt | bold | accent + hairline rule beneath |
| Entry title (role/project) | 10.5 pt | bold | ink |
| Entry meta (`Company · Dates`) | 9.3 pt | regular | muted |
| Project subtitle (no dates) | 9.2 pt | *italic* | muted |
| Body / bullets | 9.8 pt | regular | ink |
| Keyword group label | 9.3 pt | bold | ink |
| Keyword rows | 9.8 pt | regular | ink |
| Compact entry (education) | 9.8 pt | bold title + muted tail | — |
| `(continued)` label | 9.3 pt | bold | muted |
| Page number | 8 pt | regular | muted |

Colors: accent `#24456B` (dark navy — *not* bright blue), ink `#1A1A1A`,
muted `#4A4A4A`. The accent appears **only** on the name, section headings
and their rules. Body text never takes the accent.

Body leading 12.1 pt on 9.8 pt type (≈1.24). **Do not "increase line spacing
to 1.15"** — at this type size that is *tighter* than current and reads worse.
Bullets: 0 pt before, 3.0 pt after, hanging indent so wrapped lines align
with the text rather than the bullet glyph.

Margins: sides 0.65in, top 0.55in, bottom 0.5in. **Never below 0.5in** —
whitespace is part of readability.

**Do not inflate body size to 11–12 pt "so it's readable."** With this volume
of content that forces 3 pages, cramped margins, or content deletion.

### Font — LOCKED: Arial

**Arial is the default face for every resume. This is a locked decision, not
a preference.** Do not change it, and do not
reorder `FONT_CANDIDATES` to change it.

Choose faces by rendering the same resume in each and comparing side by side,
not from a spec sheet. Arial won on maximum compatibility
and neutrality.

`FONT_CANDIDATES` is a **fallback order for machines missing Arial, not a
preference ladder**:

```
Arial → Calibri → Inter → Aptos
```

Aptos sits last on purpose: if it came first, the face *and the pagination*
would change silently the moment Microsoft Office was installed. A locked
default has to actually hold.

| Face | Status |
| --- | --- |
| **Arial** | **Locked default.** Installed on Windows/macOS; maximum compatibility, most neutral. |
| Calibri | Installed on Windows. First fallback; most compact of the three, warm and slightly rounded. |
| Inter | SIL OFL, so it may be vendored. This repo ships no `resume-data/fonts/` directory; if absent, the renderers fall back to installed system fonts (ultimately Helvetica in the PDF). Modern SaaS feel. |
| Aptos | Proprietary to Microsoft 365, **cannot be vendored**. Reachable only via `--font Aptos` on a machine with Office. |

Avoid Times New Roman (academic), Poppins and Montserrat (waste horizontal
space, read as marketing collateral).

`--font` overrides the default **for comparison renders only** — the shipped
default is locked. Comparison output belongs in an `output/<slug>/variants/`
directory so it is never mistaken for a sendable document.

**Never obtain a proprietary font from a third-party mirror.** Aptos is
licensed with Microsoft 365; downloading it from a font site violates that
licence regardless of convenience. Vendored fonts must be OFL or equivalent,
with their licence file shipped alongside.

**DOCX note:** a `.docx` does not embed its font — Word substitutes whatever
the reader lacks. Arial is the right locked choice here too, since it is
present essentially everywhere; a vendored face like Inter would render as
intended only if the recipient installed it.

### Per-font optical scale

Faces differ in x-height and set width, so the same point size reads bigger and
runs wider in some than others. `FONT_SCALE` normalises both apparent size and
pagination:

```
Aptos 1.0 · Calibri 1.0 · Arial 0.97 · Inter 0.94 · Helvetica 0.97
```

Switching fonts is therefore safe: it will not silently change the page count.

### Auto-fit

`--max-pages` (default 2) searches `FIT_LADDER`, giving up **whitespace before
type size, and never content**:

```
(1.0, 1.0) → (1.0, 0.9) → (1.0, 0.8) → (0.98, 0.8)
           → (0.97, 0.75) → (0.96, 0.72) → (0.95, 0.7)
```

Each rung resolves its **own continuation set before measuring** — inserting a
repeated role heading costs real vertical space, so a setting that fits without
one can fail once it is added. Measuring the continuation-free layout is
measuring a document that never gets rendered.

If nothing fits, the renderer prints a warning and emits the tightest setting
rather than shrinking further or dropping bullets. **Deciding what to cut is
the author's call, not the renderer's.**

## Section architecture

```
PAGE 1   Name + contact
         SUMMARY                    ~4 lines, key facts bolded
         CORE COMPETENCIES          one compact "·" row, 10-12 items
         EXPERIENCE                 newest roles

PAGE 2   EXPERIENCE (continued)
         SELECTED PROJECTS
         TOOLS & TECHNICAL          grouped into 2 labeled rows
         EDUCATION & CERTIFICATION  one line per entry
```

- **Skills splits into two sections at opposite ends.** `CORE COMPETENCIES`
  (capabilities) goes high, right after the summary — scannable in 3 seconds,
  and ATS gets clean keyword density. `TOOLS & TECHNICAL` (named products and
  languages) goes low. Mixing capabilities and tool names into one paragraph
  forces the reader to parse.

- **Core Competencies caps at 10–12 items.** More becomes a keyword wall that
  defeats the purpose of a quick-scan section. This is not about deleting
  keywords from the resume — Experience already contains *operations,
  training, hiring, quality, escalation, KPI, analytics, B2B, white-label,
  process, systems, CRM, APIs, databases* in context, and contextual keywords
  serve both ATS and the human reader better than a list. **Never pad this
  section to game ATS**; a competency with no bullet behind it is an
  invitation to a question you can't answer.

- **Tools & Technical groups into labeled rows** (`**Development & Systems**`
  / `**Operations & Analytics**`), each a wholly-bold line above its `·` row.
  Grouping, not a new section — one giant tool string is unreadable.

- **Entry headings split onto two lines.** `### Title — Company | Dates`
  renders as a bold title above a quieter `Company · Dates` line, so the eye
  lands on the *role* first. A heading with no `| Dates` part is treated as a
  project: the descriptor becomes an *italic* subtitle instead.

- **Education entries collapse to one line** (bold title + muted
  `— School · Year`). Certifications are their own `###` entry, not a bullet
  under the degree — a certification is not an achievement bullet.

- **Every job entry uses the identical pattern.** Never vary formatting per
  employer; consistency is what makes progression scannable.

- **Promotions are shown with spacing, not a timeline.** Successive roles at
  the *same* employer get tight spacing (4.5 pt) while a *new* employer gets
  more air (8 pt). The renderer detects this from the company name. The eye
  reads the tight cluster as one promotion track.

## Metric bolding

The single highest-leverage change, and the easiest to overdo.

**One primary bold anchor per bullet.** Two only when a bullet genuinely
carries two separate outcomes. If every second phrase is bold, nothing is.

- Bold: **metrics, outcomes, scale, major deliverables, key systems.**
- Leave normal: explanation, methodology, background, supporting context.
- **Deliberately leave some bullets entirely unbolded.** The rhythm is what
  makes the bolded ones land.
- Prefer bolding the **result** over the mechanism. In "Built an automated
  chat assignment system to replace manual routing, cutting wait times by over
  60%", the bold belongs on the 60%, not the system name.
- Format metrics consistently: **bold number + normal descriptor**
  (**30%** overbilling, **4,500+** tickets/month). Keep digit formatting
  uniform — `4,500+` never `4500+`.
- **Use arrows for genuine before/after transformations only**: `3.6/5 → 4.5/5`,
  `8 min → under 3 min`. Never for ordinary chronology.
  The renderer preserves `→` as a real glyph (`md_to_pdf`'s substitution map
  would rewrite it to `->`).
- **Never convert bullets into mini-headings** (`**Team Growth:** Grew the
  function…`). That reads as a case study, not a resume.

## Page-break rules

Handled automatically; documented so nobody "fixes" them back:

- A section heading and its rule stay with the content beneath them.
- A role title + meta line + first bullet never split.
- The last two bullets of an entry stay together — no lone orphan bullet.
- **A bullet never breaks mid-sentence across a page.** Bullets render as
  `AtomicParagraph` (a `Paragraph` whose `split()` returns `[]`), so a bullet
  that doesn't fit moves whole to the next page. **Do not use
  `allowSplitting=0` on the document** to achieve this — it makes headings and
  keep-with-next groups atomic too, and ReportLab then raises
  "Flowable … too large on page" for groups that were always going to fit.
- When a role's bullets legitimately span a break, a quiet
  `Role Title (continued)` label is emitted at the top of the new page,
  computed from a trial build and iterated to a fixed point.

**Prefer avoiding the continuation entirely.** A page ideally begins with a
meaningful section, not a role's tail. If a role spills by only one or two
bullets, reclaim space from spacing tokens first. Accept the continuation
only when the alternative is deleting real content.

When it is unavoidable, the continuation repeats the **full role heading in
the same weight as a real entry**, with `(continued)` on the quiet meta line
only. Styled as a full heading, the page break reads as deliberate; styled as
a small grey label it reads as an apology for the previous page running out.

### On page balance

A reviewer measuring "page 1 is 75% full, page 2 is 25%" is describing a real
imbalance — but the fix is to let page 2 absorb content, never to compress
page 1 further. Once auto-fit is doing its job both pages run 90%+ full, which
is even balance, not density: roughly 2.1 pages of content in 2 pages.

**"Page 1 should feel less dense" and "2 pages" and "no content cuts" are not
simultaneously satisfiable at that volume.** Say so plainly and let the author
choose, rather than quietly shrinking type or deleting a bullet.

### When it won't fit in 2 pages

In priority order — **never delete useful content to fix a page break**:

0. **Cut padding words first.** This is the only lever that improves density
   for free, and it is reliably worth a full spacing step. Delete
   self-qualification ("unprompted", "outside role scope"), restated ideas
   ("the team's first … for the first time"), and project-documentation
   openings ("Solved a fragmentation problem first:") — see
   `resume-analyser/references/qa-checklist.md` for the full list. This
   typically buys a full spacing step while *removing no evidence*; fighting
   page pressure with spacing tokens alone hits a wall where "less dense",
   "2 pages" and "no cuts" cannot all hold. Try this before any token below.
1. Section heading `spaceBefore`, entry `spaceBefore`
2. Side margins toward 0.65in (more characters per line = fewer wrapped lines;
   often the biggest single win)
3. Body leading by 0.1–0.2 pt
4. Bullet `spaceAfter` toward 3.0 pt (the floor)
5. Body font by 0.1–0.2 pt — last resort, never below 9.5 pt

## ATS constraints (non-negotiable)

Single column · standard section headings · selectable text · embedded fonts ·
no text inside images · no tables for layout · no skill bars · no rating stars ·
no icons replacing words · no headers/footers holding real content · one bullet
style (`•`) throughout · left-aligned body, never justified (variable line
lengths produce ugly word spacing) · only the header block centered · italics
only for project subtitles · consistent en-dash date format
(`Jun 2026 – Present`) · standard job titles and company names · keywords
appearing naturally in Experience.

**Do not trade any of this for aesthetics.**

## How to apply

```bash
# Arial and a 2-page cap are the locked defaults -- no flags needed.
python .claude/skills/pdf-report/scripts/resume_to_pdf.py <resume.md> "<Role>_Your Name.pdf"
python .claude/skills/resume-docx-export/scripts/resume_to_docx.py <resume.md> "<Role>_Your Name.docx"

# CVs and cover letters are not 2-page documents -- disable the cap:
python .claude/skills/pdf-report/scripts/resume_to_pdf.py <cv.md> "<Role> - CV_Your Name.pdf" --max-pages 0
```

Both read the same `resume.md`. Never maintain separate PDF and DOCX sources.

To bring an existing profile onto this system, edit only its `resume.md`:
1. Split `## Skills` into `## Core Competencies` (after Summary, 10–12 items)
   and `## Tools & Technical` (before Education, two labeled groups).
2. Rename `## Education` → `## Education & Certification`; make each
   certification its own `###` entry.
3. Add `**bold**` around **one** metric anchor per bullet; convert genuine
   before/after pairs to `→`.
4. Normalise dates to en dashes (`Apr 2022 – May 2023`).
5. Re-render both formats.

Nothing else changes. **If a claim, number or date would need to change to
make the layout work, the layout is wrong — not the claim.**

The one legitimate grey area is *information architecture*: moving an existing
Skills paragraph into two sections is a formatting change because it
introduces no new assertion. The test — could a reader learn anything new
about the candidate from this change? If yes, it is content work and belongs
to `resume-content-optimizer`.

**A formatting pass must never silently drop content**, and equally, **an
external reviewer noticing that content changed is not proof it changed by
accident.** A reviewer may read a deliberately removed tool or claim as
formatting collateral and ask for it back; reviewers cannot see the
candidate's corrections. Check `career-bank.md`'s
zero-exposure notes before restoring anything a review asks you to put back.

## Verification (required before treating output as final)

A clean script exit is not evidence the layout is correct.

1. **Page count** — resumes target 2 pages by default.
   ```bash
   python -c "from pypdf import PdfReader; print(len(PdfReader('out.pdf').pages))"
   ```
2. **Page-break check** — print the end of each page and the start of the next;
   confirm no sentence is cut across the boundary.
3. **Font check** — confirm no Helvetica *spans* (see the command above).
4. **Arrow check** — confirm `→` survived as a glyph and no literal `->` leaked.
5. **Visual check at 100% and 150%** — render to PNG and actually look.
   ```bash
   python -c "import pymupdf,sys; d=pymupdf.open(sys.argv[1]); [p.get_pixmap(dpi=115).save(f'page-{i+1}.png') for i,p in enumerate(d)]" out.pdf
   ```
6. **Text extraction** — `pdftotext -layout out.pdf -`, confirm order and
   characters survive.

### The squint test

Read **only the bold text**, top to bottom. It should tell the career story on
its own. If it doesn't, the anchors are on the wrong words. If it reads as
noise, there are too many.

Then: can you identify the role in 3 seconds? See progression immediately?
Find the largest team, the biggest outcomes, and the differentiating achievement without
hunting? Does it still work printed in grayscale, with no color at all?
