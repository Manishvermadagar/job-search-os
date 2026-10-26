#!/usr/bin/env python3
"""
Render a resume (the same constrained Markdown convention used by
pdf-report's resume_to_pdf.py) to an ATS-safe .docx via python-docx, matching
that renderer's visual hierarchy so the two formats are recognisably the same
document. Some ATS platforms and recruiters parse/prefer DOCX, so this is a
second output format from the same source file, not a replacement.

Deliberately uses python-docx's plain paragraph/run API only -- no tables for
layout, no text boxes, no headers/footers holding real content -- for the same
reason resume_to_pdf.py avoids them: those constructs are exactly what breaks
ATS parsing. The one raw-XML touch is a bottom border on section headings and
keep-with-next, both of which are formatting attributes on ordinary
paragraphs, not structural containers.

See .claude/skills/resume-visual-format/SKILL.md for the design system.

Usage:
  python resume_to_docx.py resume.md resume.docx [--font Calibri]
"""
import argparse
import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Same tokens as resume_to_pdf.py -- keep these two files in step.
ACCENT = RGBColor(0x24, 0x45, 0x6B)
LINK = RGBColor(0x1F, 0x5F, 0xBF)  # shared token with resume_to_pdf.py LINK_HEX
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x4A, 0x4A, 0x4A)

BODY_PT = 9.8
# Design decision: Arial for every resume, matching
# resume_to_pdf.py. Arial also happens to be the safest DOCX choice, since a
# .docx does not embed its font and Word substitutes anything the reader
# lacks -- Arial is present essentially everywhere.
DEFAULT_FONT = "Arial"
# Fonts a recipient is likely to actually have. A DOCX does not embed its
# font -- Word substitutes whatever is missing -- so a vendored face like
# Inter renders correctly only if the reader installed it too.
UNIVERSAL_FONTS = {"calibri", "arial", "times new roman", "georgia", "verdana"}

KEYWORD_SECTIONS = {"core competencies", "tools & technical", "skills"}

# Entries here collapse onto one line (bold title, muted remainder).
COMPACT_SECTIONS = {"education & certification", "education",
                    "education and certification", "certifications"}


def add_run(paragraph, text, font, bold=False, italic=False, size=BODY_PT, color=INK):
    run = paragraph.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.name = font
    # East-Asian font slot too, or Word silently substitutes for some glyphs.
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    return run



URL_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)|(?<![\w/.])((?:www\.)?(?:linkedin\.com|github\.com)/[\w./-]*\w)")


def add_hyperlink(paragraph, url, text, font, size=BODY_PT, color=INK, bold=False):
    """A real w:hyperlink run; same font, size and colour as the text around it."""
    part = paragraph.part
    r_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = add_run(paragraph, text, font, bold=bold, size=size, color=LINK)
    run.underline = True
    link.append(run._element)
    paragraph._p.append(link)


def add_linked_text(paragraph, text, font, size=BODY_PT, color=INK, bold=False):
    """Plain text with profile URLs turned into hyperlinks. Mirrors resume_to_pdf.py."""
    pos = 0
    for m in URL_RE.finditer(text):
        if m.start() > pos:
            add_run(paragraph, text[pos:m.start()], font, bold=bold, size=size, color=color)
        if m.group(1):
            add_hyperlink(paragraph, m.group(2), m.group(1), font, size=size, color=color, bold=bold)
        else:
            add_hyperlink(paragraph, "https://" + m.group(3), m.group(3), font, size=size, color=color, bold=bold)
        pos = m.end()
    if pos < len(text):
        add_run(paragraph, text[pos:], font, bold=bold, size=size, color=color)


def add_inline(paragraph, text, font, size=BODY_PT, color=INK, bold=False):
    """Parse **bold** / *italic* into runs on one paragraph."""
    pos = 0
    pattern = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*")
    for m in pattern.finditer(text):
        if m.start() > pos:
            add_linked_text(paragraph, text[pos:m.start()], font, bold=bold, size=size, color=color)
        if m.group(1) is not None:
            add_run(paragraph, m.group(1), font, bold=True, size=size, color=color)
        else:
            add_run(paragraph, m.group(2), font, bold=bold, italic=True, size=size, color=color)
        pos = m.end()
    if pos < len(text):
        add_linked_text(paragraph, text[pos:], font, bold=bold, size=size, color=color)


def keep_with_next(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    el = OxmlElement("w:keepNext")
    el.set(qn("w:val"), "1")
    pPr.append(el)


def bottom_border(paragraph, hex_color="24456B", size=6):
    """Hairline rule under a section heading (a paragraph border, not a table)."""
    pPr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), hex_color)
    borders.append(bottom)
    pPr.append(borders)


def spacing(paragraph, before=0, after=0, line=None):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line:
        pf.line_spacing = Pt(line)


def set_margins(doc, inches=0.65, top=0.55, bottom=0.5):
    for section in doc.sections:
        section.top_margin = Inches(top)
        section.bottom_margin = Inches(bottom)
        section.left_margin = Inches(inches)
        section.right_margin = Inches(inches)


def split_entry_heading(raw):
    """`Title — Company | Dates` -> (title, org, dates); mirrors the PDF."""
    dates, body = "", raw
    if "|" in raw:
        body, dates = raw.rsplit("|", 1)
        body, dates = body.strip(), dates.strip()
    title, org = body, ""
    for sep in (" — ", " – ", " -- "):
        if sep in body:
            title, org = [p.strip() for p in body.split(sep, 1)]
            break
    return title.strip(), org.strip(), dates.strip()


def convert(input_path, output_path, font=DEFAULT_FONT):
    lines = Path(input_path).read_text(encoding="utf-8").split("\n")
    doc = Document()
    set_margins(doc)

    normal = doc.styles["Normal"]
    normal.font.name = font
    normal.font.size = Pt(BODY_PT)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), font)

    i, n = 0, len(lines)
    seen_name = False
    section = ""
    last_org = [None]
    # Buffered so the second-to-last bullet of an entry can be marked
    # keep-with-next, preventing a lone trailing bullet at the top of page 2.
    pending = []

    def flush_bullets():
        if len(pending) >= 2:
            keep_with_next(pending[-2])
        pending.clear()

    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        h1 = re.match(r"#\s+(.*)", stripped)
        if h1 and not seen_name:
            flush_bullets()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            spacing(p, 0, 3)
            add_run(p, h1.group(1), font, bold=True, size=24, color=ACCENT)
            seen_name = True
            i += 1
            if i < n and lines[i].strip() and not lines[i].strip().startswith("#"):
                cp = doc.add_paragraph()
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                spacing(cp, 0, 4)
                add_linked_text(cp, lines[i].strip(), font, size=9.5, color=MUTED)
                bottom_border(cp, size=10)
                i += 1
            continue

        h2 = re.match(r"##\s+(.*)", stripped)
        if h2:
            flush_bullets()
            section = h2.group(1).strip().lower()
            p = doc.add_paragraph()
            spacing(p, 7.5, 3)
            add_run(p, h2.group(1).upper(), font, bold=True, size=12.5, color=ACCENT)
            bottom_border(p)
            keep_with_next(p)
            i += 1
            continue

        h3 = re.match(r"###\s+(.*)", stripped)
        if h3:
            flush_bullets()
            title, org, dates = split_entry_heading(h3.group(1))

            if section in COMPACT_SECTIONS:
                cp = doc.add_paragraph()
                spacing(cp, 3, 0)
                add_run(cp, title, font, bold=True, color=INK)
                tail = " · ".join(x for x in (org, dates) if x)
                if tail:
                    add_run(cp, f" — {tail}", font, color=MUTED)
                i += 1
                continue

            # Successive roles at the same employer stay tight; a new employer
            # gets air, so the promotion track reads as one block.
            same_org = bool(org) and org == last_org[0]
            last_org[0] = org
            tp = doc.add_paragraph()
            spacing(tp, 4.5 if same_org else 8, 0)
            add_inline(tp, title, font, size=10.5, color=INK, bold=True)
            keep_with_next(tp)
            if org or dates:
                mp = doc.add_paragraph()
                spacing(mp, 0, 2.5)
                if org and not dates:
                    # A project descriptor, not an employer -- italic subtitle.
                    add_run(mp, org, font, italic=True, size=9.2, color=MUTED)
                else:
                    meta = " · ".join(x for x in (org, dates) if x)
                    add_run(mp, meta, font, size=9.3, color=MUTED)
                keep_with_next(mp)
            i += 1
            continue

        bullet = re.match(r"[-*]\s+(.*)", stripped)
        if bullet:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Inches(0.22)
            spacing(p, 0, 3.0)
            add_inline(p, bullet.group(1), font)
            pending.append(p)
            i += 1
            continue

        flush_bullets()
        p = doc.add_paragraph()
        if section in KEYWORD_SECTIONS and re.fullmatch(r"\*\*.+\*\*", stripped):
            spacing(p, 2, 0)
            add_run(p, stripped.strip("*"), font, bold=True, size=9.3, color=INK)
        else:
            spacing(p, 0, 1.5 if section in KEYWORD_SECTIONS else 3)
            add_inline(p, stripped, font)
        i += 1

    flush_bullets()
    doc.save(output_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Source resume Markdown file")
    parser.add_argument("output", help="Output .docx path")
    parser.add_argument("--font", default=DEFAULT_FONT,
                        help="Font family name written into the document "
                             "(Word substitutes if the reader lacks it, so "
                             "prefer a universally-installed face)")
    args = parser.parse_args()
    convert(args.input, args.output, args.font)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    sys.exit(main())
