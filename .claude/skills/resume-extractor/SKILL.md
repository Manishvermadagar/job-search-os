---
name: resume-extractor
description: Use when a candidate has an existing resume as a PDF or DOCX and needs its content pulled into editable text — usually the first step before resume-profile-manager builds a career bank, or before resume-analyser critiques content that only exists as a rendered file. Not for building a new resume from scratch (nothing to extract) — that starts directly with resume-profile-manager/resume-content-optimizer.
---

# Resume Extractor

## Why this exists

`resume-analyser` and `resume-profile-manager` both need resume content as
plain text/markdown, but real candidates almost always start from a PDF or
Word file, not a markdown source. Rather than eyeballing a rendered PDF (lossy,
easy to mis-copy a bullet), extract mechanically first.

## Process

1. Run the extractor:
   ```bash
   python3 ".claude/skills/resume-extractor/scripts/extract_text.py" <resume.pdf|resume.docx>
   ```
   PDF extraction uses `pdftotext -layout` (preserves reading order/columns
   reasonably well); DOCX extraction reads paragraphs and tables directly via
   python-docx. Neither step involves the LLM — it's mechanical text pull.
2. **Restructure the raw extraction into clean markdown yourself** — this is
   the part that needs judgment, not more code:
   - Fix reading-order artifacts (a 2-column PDF layout sometimes interleaves
     text wrong — check line order against what a human would read).
   - Identify section boundaries (SUMMARY, EXPERIENCE, EDUCATION, SKILLS —
     the original resume's own headings, even if inconsistently formatted).
   - Reconstruct bullets as `- ` lines even if the source rendered them with
     a different bullet character or as a table.
   - **Don't paraphrase or improve content during extraction** — this step
     should reproduce what's actually on the source document, word for word,
     even if it's weakly written. Improving bullets is
     `resume-content-optimizer`'s job, done deliberately later with the
     candidate's input, not silently folded into extraction.
3. Hand the cleaned markdown to whichever skill needs it next: usually
   `resume-profile-manager` (to seed/expand `career-bank.md`) or directly to
   `resume-analyser` if the candidate just wants the existing resume
   critiqued as-is.

## Known limitations

- Heavily designed resumes (multi-column, graphics-as-text, tables used for
  layout rather than data) will extract with some disorder — flag this to
  the candidate as itself a finding (`resume-analyser`'s ATS-bot persona
  would have the same problem parsing it).
- Extraction never invents or corrects content. If a bullet is genuinely
  ambiguous in the source (a metric split oddly across a line wrap), ask the
  candidate rather than guessing.
