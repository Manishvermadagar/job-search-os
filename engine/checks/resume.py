#!/usr/bin/env python3
"""resume: the tailored resume is reviewed, rendered after review, and clean.

Rendered files are checked by EXTRACTED text, never by the markdown: a phrase
fixed in resume.md survives in every PDF that was not re-rendered, and the PDF is
what an employer reads.

Banned terms are yours to set in resume-data/banned-terms.txt, one regular
expression per line (# for comments): tools you have never used, figures you
have retired, phrasings that overclaim. Demo runs use none.
"""
import glob, os, re
from common import REPO, extract_text, folder_arg, finish, intended, is_demo, nonempty, read, resolve

folder = folder_arg()
problems, notes = [], []
src = os.path.join(folder, "resume.md")
review = os.path.join(folder, "review.md")

used = []
for key, ch in intended(folder).items():
    c = ch.get("contains") or {}
    # The declared 'resume' is trusted whatever it is called (renders are named
    # <Role>_<Name>.pdf); attachments count when their name says resume or CV.
    picks = [c.get("resume")] + [a for a in (c.get("attachments") or [])
                                 if re.search(r"resume|\bcv\b", os.path.basename(str(a)), re.I)]
    for r in picks:
        if r and (key, str(r)) not in [(k, x) for k, x, _ in used]:
            used.append((key, str(r), resolve(folder, r)))

if not used:
    problems.append("no INTENDED channel records a resume. Every application needs one.")
if not nonempty(src):
    problems.append("resume.md (the tailored source) is missing in this folder")
if not nonempty(review):
    problems.append("review.md is missing - run resume-reviewer")
else:
    v = re.findall(r"VERDICT:\s*(NOT READY|READY|FAIL)", read(review), re.I)
    if not v or v[-1].upper() != "READY":
        problems.append(f"review.md's latest verdict is {v[-1].upper() if v else 'missing'}, not READY")
    elif nonempty(src) and os.path.getmtime(src) > os.path.getmtime(review) + 1:
        problems.append("resume.md changed after review.md was written - review the new version")

terms = []
tf = os.path.join(REPO, "resume-data", "banned-terms.txt")
if not is_demo(folder) and os.path.exists(tf):
    terms = [ln.strip() for ln in read(tf).splitlines() if ln.strip() and not ln.strip().startswith("#")]

renders = {p for _, _, p in used if p.lower().endswith((".pdf", ".docx"))}
renders |= set(glob.glob(os.path.join(folder, "*.pdf")) + glob.glob(os.path.join(folder, "*.docx")))
for key, rel, path in used:
    if not nonempty(path):
        problems.append(f"{key}: resume file missing or empty: {rel}")
for p in sorted(renders):
    if not os.path.exists(p):
        continue
    name = os.path.basename(p)
    if nonempty(src) and os.path.getmtime(src) > os.path.getmtime(p) + 1:
        problems.append(f"STALE RENDER: resume.md is newer than {name}. Re-render before it goes anywhere.")
    if not terms:
        continue
    text = extract_text(p)
    if text is None:
        problems.append(f"{name}: cannot extract text (install pdftotext / python-docx) to check banned terms")
        continue
    flat = re.sub(r"\s+", " ", text)
    for t in terms:
        m = re.search(t, flat, re.I)
        if m:
            problems.append(f"BANNED TERM in {name}: \"{m.group(0)}\" (pattern /{t}/ from banned-terms.txt)")

if not terms:
    notes.append("no banned terms configured" + (" (demo run)" if is_demo(folder) else
                 " - add resume-data/banned-terms.txt to check renders for them"))
finish(problems, f"resume reviewed READY; {len(renders)} render(s) fresh" + "".join("; " + n for n in notes),
       header="RESUME CHECK FAILED")
