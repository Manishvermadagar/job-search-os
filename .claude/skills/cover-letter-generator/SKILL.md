---
name: cover-letter-generator
description: Use when a candidate needs a cover letter to accompany a resume for a specific job posting — "write a cover letter for this job", "I need a cover letter to go with this resume". Depends on a finished/near-finished resume and (usually) a specific job description; not for generic "tell me about yourself" bios.
---

# Cover Letter Generator

## Process

1. Confirm that the posting and the relevant resume exist. Run
   `job-description-analyzer` if the posting has not been analyzed.
2. Treat the cover letter as a WRITE artifact. Run `question-interpreter` →
   `application-strategist` → `application-writer` → `application-verifier`,
   following `CLAUDE.md`. The writer runs `humanizer` on the draft. On a
   verifier FAIL, route the repair by failure class and repeat the writer
   and verifier passes. Do not deliver the letter until its final text passes.
3. If a PDF/DOCX is wanted, render the verified final text and verify the
   rendered content before showing it to the user.

## Hard rules

- No fabricated enthusiasm about the company beyond what's genuinely
  supportable ("excited about your mission to X" only if X is real and the
  candidate actually said this resonates — don't manufacture generic
  corporate flattery).
- No claim that isn't backed by the resume/career bank — same rule as
  `resume-content-optimizer`.
- One cover letter per application, not a generic template with the company
  name swapped — if the body paragraphs would read identically for any
  employer, it isn't tailored yet.
