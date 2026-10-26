# Pipeline reference

```
                         ┌─────────────────────┐
 existing PDF/DOCX  ───▶ │  resume-extractor    │
                         └──────────┬───────────┘
                                    ▼
                         ┌─────────────────────┐
                         │ resume-profile-      │◀── career-bank.md (one file, all real
                         │ manager               │    experience, ever-growing)
                         │  - build/expand bank  │
                         │  - define profile(s)  │◀── profiles/<slug>.md (one per role
                         │  - select_for_profile │    archetype: e.g. operations, product,
                         └──────────┬───────────┘    data analyst, ...)
                                    │  ranked bullets + summary_angle,
                                    │  per profile
                                    ▼
              ┌──────────────────────────────────┐
   job posting│  job-description-analyzer          │ (only when tailoring to one
   (optional) │  tiered keywords, req/preferred     │  specific application, on
     ────────▶│                                      │  top of the profile-level
              └──────────────────┬───────────────────┘  selection above)
                                  ▼
                       ┌─────────────────────┐
                       │ resume-content-      │
                       │ optimizer             │
                       │  - XYZ bullets        │
                       │  - metric excavation  │
                       └──────────┬───────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ humanizer             │  (strip AI-writing patterns,
                       └──────────┬───────────┘   preserve every fact)
                                  ▼
                       ┌─────────────────────┐
                       │ resume-analyser       │  (self-check gate: banned-phrase
                       │ (self-check mode)     │   scan + structural checks must
                       └──────────┬───────────┘   pass before render)
                                  ▼
                  ┌───────────────┴───────────────┐
                  ▼                                ▼
       ┌─────────────────┐              ┌─────────────────────┐
       │ pdf-report        │              │ resume-docx-export    │
       │ (resume mode)      │              │                        │
       └────────┬──────────┘              └───────────┬───────────┘
                 ▼                                     ▼
           resume.pdf                              resume.docx

  (optional, same profile's content)
                                  ▼
                       ┌─────────────────────┐
                       │ cover-letter-         │
                       │ generator              │──▶ humanizer ──▶ pdf-report
                       └─────────────────────┘
```

Everything left of `resume-content-optimizer` runs **once per profile** when
building profile-level resumes; everything from `job-description-analyzer`
onward can also run again **per specific job application** within a
profile, without re-running profile selection.
