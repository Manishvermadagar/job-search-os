---
name: resume-docx-export
description: Use to produce a .docx resume from the same resume Markdown source used for the PDF version — a second output format needed because some ATS platforms and recruiters specifically want an editable Word file rather than a PDF. Use pdf-report's resume mode for the PDF; use this alongside it, not instead of it, unless the candidate only wants one format.
---

# Resume DOCX Export

## Why this is separate from pdf-report

Different rendering library (python-docx, not reportlab), different output
format entirely — bolting a `.docx` code path onto the PDF skill would mean
one skill doing two unrelated things. Both read the *same* resume Markdown
convention, so nothing about the resume content is written twice.

## How to generate

```bash
python3 ".claude/skills/resume-docx-export/scripts/resume_to_docx.py" <resume.md> <output.docx>
```

Same input convention as `pdf-report`'s `resume_to_pdf.py`: `#` name (first
line only), the next non-blank line as the contact line, `##` section
headings, `###` role/degree entries, `-`/`*` bullets. Generate both formats
from the one `.md` file — don't maintain separate PDF-source and
DOCX-source drafts, they will drift.

## Visual design

The DOCX mirrors the PDF's design system token for token (fonts, sizes,
accent color, section architecture, keep-with-next page-break rules) so the
two formats are recognisably the same document — see
`.claude/skills/resume-visual-format/SKILL.md`. Change a token in one
renderer and you must change it in the other.

Font defaults to Calibri rather than Aptos: unlike the PDF, a DOCX does not
embed its font, so the reader's Word substitutes whatever it has. A
universally-installed face beats a nicer one that half of recipients see
replaced. Override with `--font` if the recipient is known to have Aptos.

## ATS-safety rules (same as the PDF renderer)

No tables for layout, no text boxes, no headers/footers holding real
content, no images. `resume_to_docx.py` only uses plain paragraphs, runs,
and Word's built-in "List Bullet" style — the same rules from
`resume-content-optimizer/references/ats-formatting-rules.md` apply
regardless of output format; the risk of a parser mis-reading structure is
about the file's structure, not whether it's a PDF or DOCX.

## Verification

Word documents don't get the `pdftotext` treatment `pdf-report` uses, but
apply the same spirit: open the generated `.docx` (or extract it back with
`resume-extractor`'s `extract_text.py`, which also handles `.docx`) and
confirm the content reads back cleanly and in the right order before
treating it as final — don't assume a successful script exit means the
layout is right.
