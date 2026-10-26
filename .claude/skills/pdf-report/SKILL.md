---
name: pdf-report
description: Use whenever generating a PDF in this project — a resume, CV or cover letter, or any other markdown write-up that needs to go out as a PDF. Resumes, CVs and cover letters use a dedicated ATS-safe layout (resume_to_pdf.py); everything else uses the generic markdown renderer (md_to_pdf.py).
---

# PDF Generation

Two scripts, both built on reportlab's Platypus API:

| Document | Script |
|---|---|
| Resume, CV, cover letter | `.claude/skills/pdf-report/scripts/resume_to_pdf.py` |
| Any other markdown write-up (notes, analysis, a briefing) | `.claude/skills/pdf-report/scripts/md_to_pdf.py` |

Requires `reportlab` (`pip install reportlab`). Verification uses
`pdftotext` and `pdftoppm` from poppler.

## Why reportlab Platypus

Simpler markdown-to-PDF pipelines draw table cells with low-level primitives
that do not recompute row height when text wraps, so wrapped text overflows
into neighbouring space. They also tend to break on backticks, a cell that
starts with `**bold**`, and characters outside the base font. Here, table
cells are `Paragraph` flowables: reportlab measures each wrapped cell and
grows the row to fit, so that class of bug cannot occur.

## Resume, CV and cover-letter PDFs

```bash
python3 .claude/skills/pdf-report/scripts/resume_to_pdf.py <resume.md> <output.pdf>
python3 .claude/skills/pdf-report/scripts/resume_to_pdf.py <cv.md> <output.pdf> --max-pages 0
python3 .claude/skills/pdf-report/scripts/resume_to_pdf.py <cover-letter.md> <output.pdf> --max-pages 0
```

Options: `--font` (override the face), `--no-page-numbers`, `--max-pages`
(default 2; `0` disables the fit). The fit gives up whitespace before type
size and **never drops content**; if the content cannot fit, it warns rather
than cutting. What to cut is then the user's decision.

**The typography, section architecture, emphasis rules and page-break rules
are defined in `.claude/skills/resume-visual-format/SKILL.md`.** Read it
before changing any style token here, and keep
`resume-docx-export/scripts/resume_to_docx.py` in step: the two render the
same document in two formats from shared tokens. ATS constraints are sourced
in `.claude/skills/resume-content-optimizer/references/ats-formatting-rules.md`.

Expected input shape:

- `#` for the name (first line only), and the very next non-blank line as the
  contact line;
- `##` for section headings (Summary, Core Competencies, Experience, Tools &
  Technical, Education & Certification);
- `###` for a role or degree entry, e.g. `### Title — Company | Jan 2023 - Present`;
- `-` or `*` for bullets, with one bold anchor per bullet.

No tables and no images. That is deliberate: a resume PDF a parser cannot
scramble.

**File naming.** Keep Markdown sources as `resume.md`, `cv.md` and
`cover-letter.md` inside `resume-data/output/<slug>/`, and name renders by
role and candidate name (for example `<Role>_<Full Name>.pdf`). Leave the
company out of the filename; the folder records which posting it was for.

For a `.docx` of the same resume, use the `resume-docx-export` skill. It
reads the same Markdown, so there is no second draft to maintain.

## Generic markdown PDFs

```bash
python3 .claude/skills/pdf-report/scripts/md_to_pdf.py <input.md> <output.pdf> --title "Document Title"
```

Supported subset: `#` to `####` headings; `**bold**`, `*italic*` and
`` `code` ``; pipe tables with a header row and a `---` separator row (any
column count, cells wrap automatically); `-`, `*` and `1.` list items; `---`
on its own line as a divider. Everything else is a wrapped paragraph. If a
document needs a construct outside this list (nested lists, blockquotes),
extend `md_to_pdf.py` rather than hand-editing the markdown around it.

**Unicode.** Characters outside the standard font's range are substituted
automatically (✅ → `[OK]`, ❌ → `[X]`, → → `->`; see
`UNICODE_SUBSTITUTIONS` at the top of `md_to_pdf.py`). Em dashes and curly
quotes render natively. If a new character renders as a missing-glyph box,
add it to `UNICODE_SUBSTITUTIONS`.

**Styling.** Accent colour, fonts and spacing are defined once at the top of
`md_to_pdf.py` (`ACCENT`, `ACCENT_LIGHT`, and the styles in
`build_styles()`). Change them there, not per document.

`resume_to_pdf.py` imports the Unicode-substitution and inline-formatting
helpers from `md_to_pdf.py` (same directory), so a fix there applies to both.

## Hard rule: verify every PDF before treating it as final

A clean script exit does not mean the PDF looks right. Every time a PDF is
generated or regenerated:

1. **Extract the text:** `pdftotext -layout <output.pdf> -` and look for
   leaked markup (`<b>`, `**`, `&lt;`, stray `<tag>` fragments). A match is
   an escaping bug.
2. **Check the page count** from the renderer's output or the PDF itself,
   never from a word-count estimate. Re-check after every content edit.
3. **Render a page to PNG and look at it:**
   `pdftoppm -png -r 150 -f <page> -l <page> <output.pdf> <prefix>`.
   Table wrapping, bullet indentation and page-break problems are invisible
   in extracted text. For a resume, check that wrapped (two-line) bullets
   keep their hanging indent and that no bullet splits across a page break.
4. Only after all three pass, treat the PDF as ready to show the user.

**Bullet hanging indent.** Both scripts render bullets with ReportLab's
`bulletText` parameter (`Paragraph(text, style, bulletText="•")`) and a
`bulletIndent` separate from `leftIndent`. Embedding the bullet glyph as
literal text instead makes wrapped lines start under the bullet rather than
under the text. If bullet rendering is ever changed, verify a multi-line
bullet on a rendered page; single-line bullets do not show the problem.

Rendering a PDF never sends it anywhere. Show it to the user; the user
decides where it goes.
