#!/usr/bin/env python3
"""
Convert a constrained Markdown subset to a professionally-formatted PDF using
reportlab's Platypus API. Replaces the old fpdf2 + markdown2 pipeline, whose
low-level cell renderer could not wrap table text without misaligning rows.

Supported Markdown:
  # / ## / ### / ####   headings
  **bold** / *italic* / `code`   inline formatting
  | pipe | tables |  with a header row + a --- separator row
  - bullet items   (also * and 1. / 2. numbered items, rendered as-is)
  ---   on its own line -> horizontal rule / section divider
  blank lines separate blocks; everything else is a wrapped paragraph

Usage:
  python md_to_pdf.py input.md output.pdf [--title "Report Title"]
"""
import argparse
import re
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_LEFT

ACCENT = colors.HexColor("#7A1F1F")      # heading / table-header color
ACCENT_LIGHT = colors.HexColor("#F3E6E6")  # subtle banding
GRID = colors.HexColor("#B0B0B0")

# Characters outside the standard Helvetica/WinAnsi glyph set that would
# otherwise render as a missing-glyph box. Extend this map if a new report
# introduces a character that doesn't render — don't assume it's complete.
UNICODE_SUBSTITUTIONS = {
    "✅": "[OK]",     # ✅
    "❌": "[X]",      # ❌
    "→": "->",       # →
    "←": "<-",       # ←
    "⚠": "[!]",      # ⚠
    "️": "",         # variation selector (emoji rendering hint)
    "✓": "[OK]",     # ✓
    "✗": "[X]",      # ✗
}


def substitute_unicode(text):
    for char, repl in UNICODE_SUBSTITUTIONS.items():
        text = text.replace(char, repl)
    return text


def escape_xml(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def parse_inline(text):
    """Markdown inline formatting -> reportlab Paragraph XML markup."""
    text = substitute_unicode(text)
    text = escape_xml(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"(?<!\w)\*(?!\*)(.+?)(?<!\*)\*(?!\w)", r"<i>\1</i>", text)
    return text


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"],
        textColor=ACCENT, fontSize=20, spaceAfter=14, alignment=TA_LEFT,
    ))
    for lvl, size, space_before, space_after in [
        (1, 16, 14, 8), (2, 13, 12, 6), (3, 11.5, 10, 5), (4, 10.5, 8, 4),
    ]:
        styles.add(ParagraphStyle(
            name=f"ReportHeading{lvl}", parent=styles["Normal"],
            textColor=ACCENT, fontName="Helvetica-Bold", fontSize=size,
            spaceBefore=space_before, spaceAfter=space_after, alignment=TA_LEFT,
        ))
    styles.add(ParagraphStyle(
        name="ReportBody", parent=styles["Normal"],
        fontSize=9.5, leading=13, spaceAfter=6, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="ReportBullet", parent=styles["ReportBody"],
        leftIndent=14, bulletIndent=2, spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="TableCell", parent=styles["Normal"],
        fontSize=8.2, leading=10.5, alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="TableHeaderCell", parent=styles["Normal"],
        fontSize=8.5, leading=10.5, alignment=TA_LEFT,
        textColor=colors.whitesmoke, fontName="Helvetica-Bold",
    ))
    return styles


def is_table_separator(line):
    stripped = line.strip()
    if "-" not in stripped:
        return False
    remainder = stripped.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
    return remainder == ""


def split_table_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def compute_col_widths(rows, total_width, min_width=0.55 * inch):
    ncols = len(rows[0])
    lengths = [0] * ncols
    for row in rows:
        for i, cell in enumerate(row):
            plain = re.sub(r"[*`_]", "", cell)
            lengths[i] = max(lengths[i], len(plain))
    weights = [max(min(l, 65), 5) for l in lengths]
    total_weight = sum(weights)
    widths = [total_width * w / total_weight for w in weights]
    widths = [max(w, min_width) for w in widths]
    scale = total_width / sum(widths)
    if scale < 1:
        widths = [w * scale for w in widths]
    return widths


def build_table(rows, styles, total_width):
    header, *body = rows
    col_widths = compute_col_widths(rows, total_width)
    data = [[Paragraph(parse_inline(c), styles["TableHeaderCell"]) for c in header]]
    for row in body:
        data.append([Paragraph(parse_inline(c), styles["TableCell"]) for c in row])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ACCENT_LIGHT))
    table.setStyle(TableStyle(style))
    return table


def parse_markdown(text, styles, total_width):
    lines = text.split("\n")
    story = []
    i = 0
    n = len(lines)

    def flush_paragraph(buf):
        if buf:
            joined = " ".join(l.strip() for l in buf if l.strip())
            if joined:
                story.append(Paragraph(parse_inline(joined), styles["ReportBody"]))
            buf.clear()

    para_buf = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            flush_paragraph(para_buf)
            i += 1
            continue

        # Horizontal rule / section divider
        if re.fullmatch(r"-{3,}", stripped):
            flush_paragraph(para_buf)
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=1, color=GRID))
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Headings
        heading_match = re.match(r"(#{1,4})\s+(.*)", stripped)
        if heading_match:
            flush_paragraph(para_buf)
            level = len(heading_match.group(1))
            content = heading_match.group(2)
            style_name = "ReportTitle" if level == 1 else f"ReportHeading{level}"
            story.append(Paragraph(parse_inline(content), styles[style_name]))
            i += 1
            continue

        # Table block
        if stripped.startswith("|"):
            flush_paragraph(para_buf)
            table_lines = [stripped]
            j = i + 1
            while j < n and lines[j].strip().startswith("|"):
                table_lines.append(lines[j].strip())
                j += 1
            if len(table_lines) >= 2 and is_table_separator(table_lines[1]):
                rows = [split_table_row(table_lines[0])] + [
                    split_table_row(l) for l in table_lines[2:]
                ]
                story.append(build_table(rows, styles, total_width))
                story.append(Spacer(1, 10))
            else:
                for l in table_lines:
                    story.append(Paragraph(parse_inline(l), styles["ReportBody"]))
            i = j
            continue

        # Bullet / numbered list item
        list_match = re.match(r"([-*]|\d+\.)\s+(.*)", stripped)
        if list_match:
            flush_paragraph(para_buf)
            marker, content = list_match.groups()
            bullet = "•" if marker in ("-", "*") else marker
            # bulletText (not a literal prefix) gives wrapped lines a real
            # hanging indent instead of falling back to the same flat left
            # margin as the bullet glyph -- see resume_to_pdf.py for the
            # same fix, applied there first after a rendering complaint.
            story.append(Paragraph(parse_inline(content), styles["ReportBullet"], bulletText=bullet))
            i += 1
            continue

        para_buf.append(line)
        i += 1

    flush_paragraph(para_buf)
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def convert(input_path, output_path, title=None):
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        title=title or "Report",
    )
    styles = build_styles()
    story = parse_markdown(text, styles, doc.width)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Source Markdown file")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--title", help="PDF document title metadata", default=None)
    args = parser.parse_args()

    convert(args.input, args.output, title=args.title)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    sys.exit(main())
