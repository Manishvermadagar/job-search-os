#!/usr/bin/env python3
"""
Render a resume (constrained Markdown) to an ATS-safe, single-column PDF with
a real visual hierarchy.

Separate from md_to_pdf.py's generic report renderer because a resume needs
different rules: no colored table bands, a centered name/contact header
block, and a fixed typography spec -- see
.claude/skills/resume-visual-format/SKILL.md for the design system this
implements and why (the short version: a recruiter should get role
progression, scale and measurable impact in a 10-15 second scan, which
requires size/weight/spacing/restrained-accent hierarchy, not graphics).

Expected Markdown shape:
  # Full Name
  location | phone | email                        <- contact line, right after the H1
  ## Summary
  A paragraph, with **the highest-value facts bolded**.
  ## Core Competencies
  Keyword A · Keyword B · Keyword C
  ## Experience
  ### Job Title — Company | Jan 2023 - Present    <- title/company/dates split into two visual lines
  - Bullet with **a bolded metric anchor**
  ## Selected Projects
  ### Project Name — one-line descriptor          <- no "| dates" part; descriptor becomes the meta line
  ## Tools & Technical
  Tool · Tool · Tool
  ## Education & Certification
  ### Degree — School | Year

Usage:
  python resume_to_pdf.py resume.md resume.pdf [--font Aptos] [--no-page-numbers]
"""
import argparse
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from md_to_pdf import escape_xml, substitute_unicode  # noqa: E402

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# --- Design tokens -----------------------------------------------------------
# One restrained accent, used only for the name, section headings and the rule
# beneath them. Body text stays near-black; meta lines (company/dates) sit a
# step down in weight via color, not italics.
ACCENT = colors.HexColor("#24456B")
LINK_HEX = "#1F5FBF"  # visible link blue, underlined; shared token with resume_to_docx.py LINK
INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#4A4A4A")

# Font preference order. Aptos is the target face but ships with Microsoft 365
# rather than Windows, so it is often absent; each fallback is still a
# humanist/neoclassical sans that holds up at 10pt and is ATS-safe. Helvetica
# is the built-in last resort and needs no TTF file.
# Design decision: Arial is the default face for every
# resume. It is deliberately first, not merely available -- an earlier version
# preferred Aptos and would have silently changed the face (and the pagination)
# the moment Microsoft Office was installed on any machine. A locked decision
# has to actually hold, so the chain below is a fallback order for machines
# missing Arial, NOT a preference ladder that can upgrade past it.
# Override for experiments with --font; do not reorder this list to change the
# default.
DEFAULT_FONT = "Arial"
FONT_CANDIDATES = [
    ("Arial", "arial.ttf", "arialbd.ttf", "ariali.ttf"),
    # Fallbacks, in order, for machines without Arial. Inter is vendored in
    # resume-data/fonts/ so the last real entry is always present.
    ("Calibri", "calibri.ttf", "calibrib.ttf", "calibrii.ttf"),
    ("Inter", "Inter-Regular.ttf", "Inter-Bold.ttf", "Inter-Italic.ttf"),
    ("Aptos", "aptos.ttf", "aptos-bold.ttf", "aptos-italic.ttf"),
]
# resume-data/fonts/ is checked first so a font vendored with the repo (Inter,
# SIL OFL) works on any machine without a system install. Aptos is proprietary
# to Microsoft 365 and cannot be vendored -- if Office is installed it is found
# in the system directories below and wins automatically.
# Faces differ in x-height and set width, so the same point size reads bigger
# and runs wider in some than others. These factors normalise apparent size AND
# pagination across the options -- Inter in particular has a large x-height and
# needs ~6% less to match Calibri optically.
FONT_SCALE = {"Aptos": 1.0, "Calibri": 1.0, "Arial": 0.97, "Inter": 0.94,
              "Helvetica": 0.97}

FONT_DIRS = [
    Path(__file__).resolve().parents[4] / "resume-data" / "fonts",
    Path("C:/Windows/Fonts"),
    Path.home() / "AppData/Local/Microsoft/Windows/Fonts",
    Path("/usr/share/fonts"),
    Path("/Library/Fonts"),
    Path.home() / "Library/Fonts",
]


def _find_font_file(filename):
    for d in FONT_DIRS:
        if not d.exists():
            continue
        direct = d / filename
        if direct.exists():
            return direct
        # Linux keeps fonts in nested per-family directories.
        for hit in d.rglob(filename):
            return hit
    return None


def register_font(preferred=None):
    """Register the best available TTF family; return (regular, bold) names.

    Registering a real family (rather than leaning on the built-in Type 1
    faces) is what lets <b> inside a Paragraph resolve to the true bold cut
    and keeps the bullet glyph from falling out of the encoding.
    """
    candidates = FONT_CANDIDATES
    preferred = preferred or DEFAULT_FONT
    if preferred:
        candidates = (
            [c for c in FONT_CANDIDATES if c[0].lower() == preferred.lower()]
            + [c for c in FONT_CANDIDATES if c[0].lower() != preferred.lower()]
        )
    for family, reg, bold, ital in candidates:
        reg_path, bold_path = _find_font_file(reg), _find_font_file(bold)
        if not (reg_path and bold_path):
            continue
        ital_path = _find_font_file(ital)
        pdfmetrics.registerFont(TTFont(family, str(reg_path)))
        pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(bold_path)))
        if ital_path:
            pdfmetrics.registerFont(TTFont(f"{family}-Italic", str(ital_path)))
        pdfmetrics.registerFontFamily(
            family,
            normal=family,
            bold=f"{family}-Bold",
            italic=f"{family}-Italic" if ital_path else family,
            boldItalic=f"{family}-Bold",
        )
        return (family, f"{family}-Bold",
                f"{family}-Italic" if ital_path else family)
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


# md_to_pdf's map rewrites "→" to "->" because its built-in Helvetica can't
# render the glyph. This renderer embeds a real TTF that can, and arrows are
# load-bearing here (3.6/5 → 4.5/5 reads far faster than the prose version), so
# arrows are excluded from substitution.
_KEEP = {"→", "←"}


class AtomicParagraph(Paragraph):
    """A Paragraph that refuses to break across a page.

    Scoped to bullets deliberately. Setting `allowSplitting=0` on the whole
    document also makes headings, rules and keep-with-next groups atomic,
    which makes ReportLab raise "too large on page" for groups that were
    always going to be fine -- and it is only bullets that must not split. A
    bullet cut mid-sentence ("...from job post" / "through onboarding.") is
    the single most visible layout defect a resume can have; returning no
    split points sends the whole bullet to the next page instead.
    """

    def split(self, availWidth, availHeight):
        return []


def parse_inline(text):
    text = "".join(c if c in _KEEP else substitute_unicode(c) for c in text)
    text = escape_xml(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\w)\*(?!\*)(.+?)(?<!\*)\*(?!\w)", r"<i>\1</i>", text)
    # Bare profile URLs (linkedin.com/..., github.com/...) become clickable; the visible
    # text is unchanged so ATS parsing sees the same string. Mirrored in resume_to_docx.py.
    # [Label](https://url) renders the label as a clickable word. Mirrored in resume_to_docx.py.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<link href="\2"><font color="%s"><u>\1</u></font></link>' % LINK_HEX, text)
    text = re.sub(r"(?<![\w/.\"])((?:www\.)?(?:linkedin\.com|github\.com)/[\w./-]*\w)(?![^<]*</link>)",
                  r'<link href="https://\1"><font color="%s"><u>\1</u></font></link>' % LINK_HEX, text)
    return text


def build_styles(regular, bold, italic, scale=1.0, space=1.0):
    """Build the style sheet.

    `scale` multiplies every type size and leading (per-font optical
    correction); `space` multiplies every vertical gap. convert() searches over
    both to fit a target page count without touching content.
    """
    styles = getSampleStyleSheet()
    ours = []

    def add(style):
        # Scaling happens once, after every style is built. Doing it inside
        # add() would double-scale any style declared with parent=<one of ours>,
        # since ReportLab resolves parent attributes at construction time and
        # the child would inherit an already-scaled value.
        ours.append(style)
        styles.add(style)
    add(ParagraphStyle(
        name="Name", parent=styles["Normal"], fontName=bold,
        fontSize=24, leading=27, alignment=TA_CENTER, textColor=ACCENT,
        spaceAfter=3,
    ))
    add(ParagraphStyle(
        name="Contact", parent=styles["Normal"], fontName=regular,
        fontSize=9.3, leading=12, alignment=TA_CENTER, textColor=MUTED,
        spaceAfter=4,
    ))
    # Generous space BEFORE a section heading, tight after: whitespace groups
    # the heading with what follows instead of floating between blocks.
    add(ParagraphStyle(
        name="SectionHeading", parent=styles["Normal"], fontName=bold,
        fontSize=12.5, leading=14.5, alignment=TA_LEFT, textColor=ACCENT,
        spaceBefore=8.5, spaceAfter=2.5,
    ))
    # Role/degree/project title -- the strongest weight below the section rule.
    # Two variants: successive roles at the SAME employer sit tight together so
    # they read as one promotion track; a new employer gets extra air.
    add(ParagraphStyle(
        name="EntryTitle", parent=styles["Normal"], fontName=bold,
        fontSize=10.5, leading=12.6, alignment=TA_LEFT, textColor=INK,
        spaceBefore=8.5, spaceAfter=0,
    ))
    add(ParagraphStyle(
        name="EntryTitleNewOrg", parent=styles["EntryTitle"], spaceBefore=11,
    ))
    # Company · dates -- deliberately a step quieter so the eye lands on the
    # title, then the metrics, then the prose.
    add(ParagraphStyle(
        name="EntryMeta", parent=styles["Normal"], fontName=regular,
        fontSize=9.5, leading=11.8, alignment=TA_LEFT, textColor=MUTED,
        spaceAfter=4,
    ))
    # Project descriptor (no dates) -- italic, so it reads as a subtitle rather
    # than as another employer/date line.
    add(ParagraphStyle(
        name="EntrySubtitle", parent=styles["EntryMeta"], fontName=italic,
        fontSize=9.2,
    ))
    add(ParagraphStyle(
        name="Body", parent=styles["Normal"], fontName=regular,
        fontSize=9.8, leading=12.15, alignment=TA_LEFT, textColor=INK,
        spaceAfter=5,
    ))
    # Keyword rows (Core Competencies, Tools & Technical) run long and are
    # scanned, not read -- tighter leading keeps them to a compact block.
    add(ParagraphStyle(
        name="KeywordRow", parent=styles["Body"], leading=12.4, spaceAfter=2,
    ))
    # Group label inside Tools & Technical ("Development & Systems").
    add(ParagraphStyle(
        name="KeywordLabel", parent=styles["Body"], fontName=bold,
        fontSize=9.3, leading=11.6, textColor=INK, spaceBefore=2, spaceAfter=0,
    ))
    # bulletFontName must be set explicitly: ReportLab defaults it to Helvetica
    # regardless of the paragraph font, which silently embedded a second font
    # family into every resume just to draw the bullet glyphs.
    add(ParagraphStyle(
        name="ResumeBullet", parent=styles["Body"], leftIndent=13,
        bulletIndent=1, spaceAfter=2.6, bulletFontName=regular,
        bulletFontSize=9.8,
    ))
    # Education / certification: one line each, bold title + muted remainder.
    add(ParagraphStyle(
        name="CompactEntry", parent=styles["Body"], fontName=regular,
        fontSize=9.8, leading=12.3, spaceBefore=3, spaceAfter=0,
    ))
    # A role continuing onto a new page repeats its heading in the SAME weight
    # as a real entry, with "(continued)" only on the quiet meta line. Styling
    # it as a full heading is what makes the page break read as deliberate.
    add(ParagraphStyle(
        name="ContinuedTitle", parent=styles["EntryTitle"],
        spaceBefore=0, spaceAfter=0,
    ))
    add(ParagraphStyle(
        name="Continued", parent=styles["EntryMeta"],
        spaceBefore=0, spaceAfter=5,
    ))

    if scale != 1.0 or space != 1.0:
        for st in ours:
            for attr, mult in (("fontSize", scale), ("leading", scale),
                               ("bulletFontSize", scale),
                               ("spaceBefore", space), ("spaceAfter", space)):
                v = getattr(st, attr, None)
                if v:
                    setattr(st, attr, round(v * mult, 2))
    return styles


# Sections whose body text is a "·"-separated scan row rather than prose.
KEYWORD_SECTIONS = {"core competencies", "tools & technical", "skills"}

# Sections whose entries collapse onto ONE line (bold title, muted remainder).
# Education and certifications carry little weight this far into a career and
# should not consume three lines each the way a role does.
COMPACT_SECTIONS = {"education & certification", "education",
                    "education and certification", "certifications"}


def split_entry_heading(raw):
    """`Title — Company | Dates` -> (title, org, dates).

    Falls back gracefully: a heading with no separator is all title, and a
    project heading (`Name — descriptor`, no `|`) yields an org with no dates,
    which the caller renders as an italic subtitle instead of a meta line.
    """
    dates = ""
    body = raw
    if "|" in raw:
        body, dates = raw.rsplit("|", 1)
        body, dates = body.strip(), dates.strip()
    title, org = body, ""
    for sep in (" — ", " – ", " -- "):
        if sep in body:
            title, org = [p.strip() for p in body.split(sep, 1)]
            break
    return title.strip(), org.strip(), dates.strip()


def parse_resume(text, styles, continuations=frozenset()):
    """Build the flowable story.

    `continuations` holds bullet sequence numbers that should be preceded by a
    "<Role> (continued)" label -- computed by convert() from a trial build, so
    a role whose bullets run over a page break re-announces itself instead of
    dumping context-free bullets at the top of page 2.
    """
    lines = text.split("\n")
    story = []
    i, n = 0, len(lines)
    seen_name = False
    section = ""
    seq = [0]              # bullet counter, stable across passes
    current_entry = [("", "")]  # (title, meta) for continuation headings
    last_org = [None]      # drives same-employer vs new-employer spacing

    def new_bullet(body):
        p = AtomicParagraph(parse_inline(body), styles["ResumeBullet"], bulletText="•")
        p._seq = seq[0]
        p._entry = current_entry[0]
        seq[0] += 1
        return p
    # Bullets are buffered per entry so the last two can be kept together --
    # a role whose final bullet lands alone at the top of page 2 reads as an
    # orphaned fragment, which was the single worst artifact of the old layout.
    pending_bullets = []

    def flush_bullets():
        if not pending_bullets:
            return
        # keepWithNext rather than KeepTogether: KeepTogether hands the whole
        # group to the page as one flowable, which both defeats afterFlowable's
        # per-bullet page tracking and can shove a long role wholesale onto the
        # next page. keepWithNext binds only the pairs that matter.
        if len(pending_bullets) >= 2:
            pending_bullets[-2].keepWithNext = 1   # no lone trailing bullet
        for p in pending_bullets:
            entry = getattr(p, "_entry", ("", ""))
            title, meta = entry if isinstance(entry, tuple) else (entry, "")
            if getattr(p, "_seq", None) in continuations and title:
                # Repeat the full role heading, styled like a real entry, so the
                # page opens on something that looks intended rather than on an
                # apology for the previous page running out of room. Both parts
                # bind to the bullet so they can never strand at a page foot.
                head = Paragraph(parse_inline(title), styles["ContinuedTitle"])
                head.keepWithNext = 1
                story.append(head)
                if meta:
                    sub = Paragraph(
                        f"<b>{parse_inline(meta.split(' · ')[0])}</b>"
                        f"{parse_inline(meta[len(meta.split(' · ')[0]):])} (continued)",
                        styles["Continued"])
                    sub.keepWithNext = 1
                    story.append(sub)
            story.append(p)
        pending_bullets.clear()

    para_buf = []

    def flush_para():
        if para_buf:
            joined = " ".join(l.strip() for l in para_buf if l.strip())
            if joined:
                style = "Body"
                if section in KEYWORD_SECTIONS:
                    # A line that is nothing but bold text is a group label,
                    # not a keyword row.
                    style = ("KeywordLabel"
                             if re.fullmatch(r"\*\*.+\*\*", joined)
                             else "KeywordRow")
                story.append(Paragraph(parse_inline(joined), styles[style]))
            para_buf.clear()

    def flush_all():
        flush_para()
        flush_bullets()

    while i < n:
        stripped = lines[i].strip()

        if not stripped:
            flush_para()
            i += 1
            continue

        h1 = re.match(r"#\s+(.*)", stripped)
        if h1 and not seen_name:
            flush_all()
            story.append(Paragraph(parse_inline(h1.group(1)), styles["Name"]))
            seen_name = True
            i += 1
            if i < n and lines[i].strip() and not lines[i].strip().startswith("#"):
                story.append(Paragraph(parse_inline(lines[i].strip()), styles["Contact"]))
                i += 1
            story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                                    spaceBefore=4, spaceAfter=0))
            continue

        h2 = re.match(r"##\s+(.*)", stripped)
        if h2:
            flush_all()
            section = h2.group(1).strip().lower()
            # Heading first, hairline rule beneath it: the rule closes the
            # heading and opens the block, which reads as one unit. (The old
            # layout put the rule above, orphaning headings from their rules
            # at page breaks.)
            heading = Paragraph(parse_inline(h2.group(1).upper()), styles["SectionHeading"])
            rule = HRFlowable(width="100%", thickness=0.6, color=ACCENT,
                              spaceBefore=0, spaceAfter=4)
            heading.keepWithNext = rule.keepWithNext = 1
            story.extend([heading, rule])
            i += 1
            continue

        h3 = re.match(r"###\s+(.*)", stripped)
        if h3:
            flush_all()
            title, org, dates = split_entry_heading(h3.group(1))
            current_entry[0] = (title, " · ".join(x for x in (org, dates) if x))

            if section in COMPACT_SECTIONS:
                tail = " · ".join(p for p in (org, dates) if p)
                markup = f"<b>{parse_inline(title)}</b>"
                if tail:
                    markup += (f' <font color="#{MUTED.hexval()[2:]}">'
                               f"— {parse_inline(tail)}</font>")
                story.append(Paragraph(markup, styles["CompactEntry"]))
                i += 1
                continue
            # Successive roles at the same employer stay visually tight so the
            # promotion track reads as one block; a new employer gets air.
            same_org = bool(org) and org == last_org[0]
            last_org[0] = org
            block = [Paragraph(
                parse_inline(title),
                styles["EntryTitle" if same_org else "EntryTitleNewOrg"],
            )]
            if org and dates:
                # Company bolded, date left plain: the employer is the scan
                # target, the date is reference detail.
                block.append(Paragraph(
                    f"<b>{parse_inline(org)}</b> · {parse_inline(dates)}",
                    styles["EntryMeta"]))
            elif dates:
                block.append(Paragraph(parse_inline(dates), styles["EntryMeta"]))
            elif org:
                # No dates -> this is a project descriptor, not an employer.
                block.append(Paragraph(parse_inline(org), styles["EntrySubtitle"]))
            # Pull the first bullet up into the heading block so a role title
            # can never sit alone at the foot of a page.
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            first = re.match(r"[-*]\s+(.*)", lines[j].strip()) if j < n else None
            if first:
                block.append(new_bullet(first.group(1)))
                i = j + 1
            else:
                i += 1
            for f in block[:-1]:
                f.keepWithNext = 1
            story.extend(block)
            continue

        bullet = re.match(r"[-*]\s+(.*)", stripped)
        if bullet:
            flush_para()
            pending_bullets.append(new_bullet(bullet.group(1)))
            i += 1
            continue

        # A wholly-bold line inside a keyword section is a group label
        # ("**Development & Systems**") and owns its own line -- without this
        # it merges into the keyword row below it, which is exactly the
        # undifferentiated tool-string the grouping exists to break up.
        if section in KEYWORD_SECTIONS and re.fullmatch(r"\*\*.+\*\*", stripped):
            flush_para()
            story.append(Paragraph(parse_inline(stripped), styles["KeywordLabel"]))
            i += 1
            continue

        flush_bullets()
        para_buf.append(lines[i])
        i += 1

    flush_all()
    return story


def make_footer(regular, enabled):
    def footer(canvas, doc):
        if not enabled:
            return
        canvas.saveState()
        canvas.setFont(regular, 8)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(letter[0] / 2.0, 0.42 * inch, str(doc.page))
        canvas.restoreState()
    return footer


class _RecordingDoc(SimpleDocTemplate):
    """SimpleDocTemplate that records which page each bullet landed on."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.bullet_pages = {}

    def afterFlowable(self, flowable):
        seq = getattr(flowable, "_seq", None)
        if seq is not None:
            self.bullet_pages[seq] = self.page


def _needed_continuations(text, styles, doc_factory, continuations, footer):
    """Trial-build and return the bullet seqs that open an entry on a new page."""
    story = parse_resume(text, styles, continuations)
    # Sequence numbers are deterministic for a given markdown source, so the
    # mapping survives the rebuild that the real render does.
    seq_entry = {f._seq: getattr(f, "_entry", "")
                 for f in story if getattr(f, "_seq", None) is not None}
    doc = doc_factory(io.BytesIO())
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    needed, prev_page, prev_entry = set(), None, None
    for seq in sorted(doc.bullet_pages):
        page, entry = doc.bullet_pages[seq], seq_entry.get(seq) or ""
        if prev_page is not None and page != prev_page and entry and entry == prev_entry:
            needed.add(seq)
        prev_page, prev_entry = page, entry
    return needed


# Tried in order until the document fits `max_pages`. Vertical space is given
# up before type size, because whitespace degrades more gracefully than
# legibility -- and neither ever gives up content.
FIT_LADDER = [(1.0, 1.0), (1.0, 0.9), (1.0, 0.8), (0.98, 0.8),
              (0.97, 0.75), (0.96, 0.72), (0.95, 0.7)]


def _page_count(text, styles, doc_factory, footer, continuations):
    doc = doc_factory(io.BytesIO())
    doc.build(parse_resume(text, styles, continuations),
              onFirstPage=footer, onLaterPages=footer)
    return doc.page


def convert(input_path, output_path, preferred_font=None, page_numbers=True,
            max_pages=2):
    regular, bold, italic = register_font(preferred_font)
    text = Path(input_path).read_text(encoding="utf-8")
    footer = make_footer(regular, page_numbers)
    scale0 = FONT_SCALE.get(regular, 1.0)

    def doc_factory(target):
        return _RecordingDoc(
            target, pagesize=letter,
            topMargin=0.55 * inch, bottomMargin=0.5 * inch,
            leftMargin=0.65 * inch, rightMargin=0.65 * inch,
            title=Path(output_path).stem,
        )

    def resolve(styles):
        """Settle the continuation set for these styles, and report page count.

        Continuations must be resolved *inside* the fit search, not before it:
        inserting a repeated role heading costs real vertical space, so a
        setting that fits without one can fail once it is added. Measuring the
        continuation-free layout is measuring a document we never render.
        """
        continuations = frozenset()
        for _ in range(3):
            needed = frozenset(
                _needed_continuations(text, styles, doc_factory, continuations, footer))
            if needed == continuations:
                break
            continuations = needed
        doc = doc_factory(io.BytesIO())
        doc.build(parse_resume(text, styles, continuations),
                  onFirstPage=footer, onLaterPages=footer)
        return continuations, doc.page

    ladder = FIT_LADDER if max_pages else [(1.0, 1.0)]
    chosen = None
    for sc, sp in ladder:
        styles = build_styles(regular, bold, italic, scale0 * sc, sp)
        continuations, pages = resolve(styles)
        chosen = (styles, continuations, pages, sc, sp)
        if not max_pages or pages <= max_pages:
            break

    styles, continuations, pages, sc, sp = chosen
    if max_pages and pages > max_pages:
        # Say so rather than shrinking further or dropping content -- deciding
        # what to cut is the author's call, not the renderer's.
        print(f"  warning: {pages} pages at the tightest setting "
              f"(scale {sc}, spacing {sp}); content exceeds {max_pages} pages",
              file=sys.stderr)

    doc_factory(output_path).build(
        parse_resume(text, styles, continuations),
        onFirstPage=footer, onLaterPages=footer,
    )
    return regular, pages, sc, sp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Source resume Markdown file")
    parser.add_argument("output", help="Output PDF path")
    parser.add_argument("--font", default=None,
                        help=f"Override the locked default ({DEFAULT_FONT}). "
                             "Available: Arial, Calibri, Inter, Aptos (Aptos "
                             "only if Microsoft Office is installed). For "
                             "comparison renders only -- the shipped default "
                             "is a locked decision.")
    parser.add_argument("--no-page-numbers", action="store_true")
    parser.add_argument("--max-pages", type=int, default=2,
                        help="Auto-fit to at most this many pages by giving up "
                             "whitespace then type size, never content. 0 disables.")
    args = parser.parse_args()
    used, pages, sc, sp = convert(args.input, args.output, args.font,
                                  not args.no_page_numbers, args.max_pages)
    fit = "" if (sc, sp) == (1.0, 1.0) else f", fit: type x{sc} space x{sp}"
    print(f"Wrote {args.output} (font: {used}, {pages} pages{fit})")


if __name__ == "__main__":
    sys.exit(main())
