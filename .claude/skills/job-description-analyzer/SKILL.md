---
name: job-description-analyzer
description: Use to break down a job posting into required/preferred qualifications and tiered keywords before tailoring a resume or cover letter to it. Called by resume-content-optimizer, resume-profile-manager, and cover-letter-generator — rarely invoked standalone unless the user just wants to understand a posting on its own ("what is this JD actually asking for").
---

# Job Description Analyzer

## Why this is its own skill

Three different skills need the same JD breakdown (content optimizer, profile manager when scoring which profile a
posting matches, cover-letter generator) — duplicating the extraction logic
three times would have meant three places to fix if the tiering rule needed
adjusting.

## Process

1. Save the job posting text to a file (paste-to-file if the user pasted it
   inline).
2. Keep the full posting verbatim, but run deterministic tiering on its role
   responsibilities and qualifications only. Exclude employer background,
   listing metadata and application questions from the analysis input:
   ```bash
   python3 ".claude/skills/job-description-analyzer/scripts/parse_jd.py" <role-requirements.txt>
   ```
   The frequency tiers are review candidates, not requirements. Report the
   computed counts, then identify which terms describe the role and are
   supported by the career bank. Never require an employer name, form wording
   or an unsupported candidate claim to appear in the resume.
3. **Add judgment on top of the computed tiers** — the script doesn't know
   what it doesn't know:
   - Infer the role archetype (e.g. "growth-focused B2B SaaS PM" vs.
     "technical/platform PM") — this matters for `resume-profile-manager`
     matching the posting to an existing profile or flagging that a new
     profile is needed.
   - Read the required-lines/preferred-lines split for accuracy — the
     heading-detection heuristic is coarse; recategorize anything obviously
     misbucketed.
   - Note domain jargon or company-specific terms the frequency count would
     miss because they only appear once but clearly matter (e.g. a named
     internal methodology, a specific compliance framework).
4. Hand off the combined result (computed tiers + judgment additions) to
   whichever skill invoked this one — don't just paste the raw script output
   without the judgment pass, and don't silently override the computed tiers
   with a guess instead.
5. When the analysis is for an application, save the posting verbatim as
   `resume-data/output/<slug>/jd-posting.txt` — including listing metadata
   that is not in the JD body (compensation band, experience filter,
   location or remote terms, apply-to address) — and the combined analysis
   as `jd-analysis.md` in the same folder. If the board's structured fields
   contradict the employer's own wording, record both; the employer's words
   are authoritative.

## What this skill does not do

Doesn't rewrite resume content and doesn't decide whether a candidate should
apply — it only characterizes the posting. For content tailoring, that's
`resume-content-optimizer`; for deciding which existing profile (if any) a
posting matches, that's `resume-profile-manager`.
