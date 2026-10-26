# ATS-safe formatting rules

Sourced primarily from dabydat/resume-builder-skill's `format-and-structure.md`
(itself cross-referenced against Harvard's career-services guide, the
r/EngineeringResumes wiki, and Gergely Orosz's "The Tech Resume Inside Out" —
that repo's `SOURCES.md` was the only one of 8 surveyed that documented where
each rule actually came from and flagged disagreements between sources).

## Layout
- Single column, always. No tables, text boxes, columns, headers/footers,
  images, icons, or graphics for content that matters — a parser reads text
  in document order and multi-column layouts get interleaved wrong.
- Standard section headings only: "Experience" / "Professional Experience",
  "Education", "Skills" / "Technical Skills", "Projects". Not "My Journey" or
  "What I Bring" — a parser matches against a known header vocabulary.
- Contact info (name, phone, email, location, LinkedIn/portfolio URL) in the
  body text, not in a header/footer field — many parsers skip headers/footers
  entirely.
- Consistent date format throughout (e.g. "Jan 2023 – Present", en-dash, not
  a mix of "1/23", "January 2023", "23").

## Section order
Skills first for technical/engineering roles (per Harvard's "order headings
by importance" guidance and confirmed by r/EngineeringResumes practice) —
Experience → Projects → Education, with Education moving to the bottom once
the candidate has 3+ years of experience. For non-technical roles, lead with
Experience, Skills lower.

## Bullet formatting and readability
Sourced from a live web check of current (2026) ATS/resume-formatting
guidance (Jobscan, ResumeAdapter, hireflow, ResuFit) after a real rendered
resume showed cluttered wrapped bullets — see `pdf-report/SKILL.md`'s
"Bullet hanging-indent bug" entry for the rendering-side root cause and fix.
- Standard bullet glyphs only (•, -, or *) — arrow/decorative bullets are
  usually ATS-safe too but standard dots/dashes are the safer default.
- Wrapped (2+ line) bullets need a real hanging indent: the bullet glyph
  sits at its own left position, and every line of the bullet's text —
  including wrapped continuation lines — aligns to one consistent left
  margin *after* the bullet, not back at the bullet's own margin. A bullet
  that wraps to a new line starting under the bullet glyph itself (instead
  of under the text) reads as cluttered even though the words are correct —
  this is a rendering check, not a text-extraction check; catch it by
  looking at an actual rendered page with a wrapped bullet on it, not by
  reading extracted text alone.
- 3–6pt spacing between bullets — enough to keep bullets visually distinct
  without the resume feeling sparse; single (1.0) line spacing within a
  bullet's own wrapped lines.
- Keep bullets to 1–2 lines each where possible. A "wall of text" bullet
  running 3+ lines is unreadable at scanning speed regardless of indent
  correctness — this is a drafting-stage rule (trim the bullet), not
  something a rendering fix can solve on its own.
- Clean single-column layout beats a more "designed" layout that risks
  hiding real qualifications from a parser, even when the fancier layout
  looks nicer to a human on first glance.

## Typography (when generating a PDF/DOCX)
- Name: ~16pt. Section headings: ~11.5pt bold. Body: ~9.5–10.5pt.
- Standard fonts only (Calibri, Arial, Helvetica, Times New Roman) — a
  decorative or embedded font can fail to parse or substitute badly.
- 0.75in margins as a default; only compress further if content genuinely
  doesn't fit at 1 page for <3 years experience / 2 pages for senior roles.

## Page length
General rule: 1 page for <10 years experience unless the field expects
otherwise (academic CVs are the standing exception); 2 pages acceptable for
senior/staff+ roles with 10+ years, per Orosz and Harvard.

**Default in this repo: resumes build to 2 pages**, not 1. A one-page draft is often too thin to show real depth. Earn the second page with verified content only (never pad); `analyze_resume.py --doctype resume` scores ~2 pages as the target. CVs are unaffected.

## What NOT to do (the actual myth to debunk)
"ATS rejects most resumes before a human sees them" is a widely-repeated,
unsourced stat — no credible source for a specific percentage exists. Modern
ATS platforms (Workday, Greenhouse, Taleo, iCIMS) are databases with search/
filter/rank features; they very rarely auto-reject on parsing failure alone.
The real risk is a parsing failure that scrambles or drops content so a human
reviewer sees garbage — that's what these rules actually prevent, not an
imaginary robot gatekeeper.
