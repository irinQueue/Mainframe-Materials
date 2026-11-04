"""Render a side-by-side comparison review as Markdown + PDF.

The layout is fixed: title and subtitle, "What we compared", a verdict call-out,
"What is the same", a 1-5 scorecard with a "Better" column and an average row,
plain-language differences tagged by which side is safer, an optional sample
output table, shared problems, a two-column production sign-off table,
housekeeping, next steps and a glossary. Portrait US Letter, navy headers,
green shading for side A, blue for side B.

Usage:
    python -I comparison_report.py <content.json> <output_dir>

Writes <output_dir>/<output_name>.md and <output_dir>/<output_name>.pdf.
See report_content_template.json for every field. Text fields may use the
ReportLab inline tags <b>, <i> and <font>; they are converted for Markdown.
Requires reportlab.
"""
import json
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

NAVY = colors.HexColor("#1F3A5F")
SIDE_A_FILL = colors.HexColor("#DFF0E5")
SIDE_B_FILL = colors.HexColor("#E1EAF7")
TIE_FILL = colors.HexColor("#F1F1F1")
GRID = colors.HexColor("#B8C2CC")
CALLOUT_FILL = colors.HexColor("#FFF6E0")
CALLOUT_EDGE = colors.HexColor("#E0C27A")
TAG_A, TAG_B, TAG_MIXED, TAG_DECIDE = "#2E7D4F", "#2F5DA8", "#7A7A7A", "#B26B00"


def to_md(html: str) -> str:
    for a, b in (("<b>", "**"), ("</b>", "**"), ("<i>", "*"), ("</i>", "*"),
                 ("&nbsp;", " ")):
        html = html.replace(a, b)
    return re.sub(r"</?font[^>]*>", "", html)


def better(a: float, b: float, c: dict) -> str:
    return c["side_a"] if a > b else c["side_b"] if b > a else "Tie"


def averages(c: dict):
    s = c["scores"]
    return (sum(r[1] for r in s) / len(s), sum(r[2] for r in s) / len(s))


def write_markdown(c: dict, path: Path) -> None:
    A, B = c["side_a"], c["side_b"]
    md = [f"# {c['title']}", "", f"*{c['subtitle']}*", "",
          "## What we compared", "", to_md(c["intro"]), "",
          "## The verdict", ""]
    md += [f"- {to_md(v)}" for v in c["verdict"]]
    md += ["", "## What is the same", ""]
    md += [f"- {to_md(s)}" for s in c["same"]]
    md += ["", "## Senior developer's scorecard (1 = poor, 5 = excellent)",
           "", f"| Area | {A} | {B} | Better | Why |", "|---|---|---|---|---|"]
    for area, a, b, why in c["scores"]:
        md.append(f"| {area} | {a} | {b} | {better(a, b, c)} | {why} |")
    ta, tb = averages(c)
    md.append(f"| **Average** | **{ta:.1f}** | **{tb:.1f}** | "
              f"**{better(ta, tb, c)}** | {c.get('average_note', '')} |")
    md += ["", "## The main differences, in plain words", ""]
    for head, tag, body in c["differences"]:
        md += [f"**{head}** *({tag})*  ", to_md(body), ""]
    so = c.get("sample_output")
    if so:
        md += ["## Sample output comparison", "", to_md(so["intro"]), "",
               "| " + " | ".join(so["columns"]) + " |",
               "|" + "---|" * len(so["columns"])]
        md += ["| " + " | ".join(to_md(x) for x in r) + " |"
               for r in so["rows"]]
        md.append("")
    if c.get("shared"):
        md += ["## Problems both versions share", ""]
        md += [f"- {to_md(s)}" for s in c["shared"]] + [""]
    md += ["## Production sign-off: what must change first", "",
           to_md(c.get("fix_intro", "")), "", f"**{A}**", ""]
    md += [f"- {to_md(s)}" for s in c["fix_a"]]
    md += ["", f"**{B}**", ""] + [f"- {to_md(s)}" for s in c["fix_b"]]
    if c.get("housekeeping"):
        md += ["", "## Housekeeping", ""]
        md += [f"- {to_md(s)}" for s in c["housekeeping"]]
    md += ["", "## Recommended next steps", ""]
    md += [f"{i}. {to_md(s)}" for i, s in enumerate(c["next_steps"], 1)]
    md += ["", "## Glossary", "", "| Term | Meaning |", "|---|---|"]
    md += [f"| {t} | {d} |" for t, d in c["glossary"]]
    path.write_text("\n".join(md) + "\n", encoding="utf-8")


def write_pdf(c: dict, path: Path) -> None:
    A, B = c["side_a"], c["side_b"]
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                          fontSize=10, leading=14, alignment=TA_LEFT)
    small = ParagraphStyle("small", parent=body, fontSize=9, leading=12)
    small_c = ParagraphStyle("small_c", parent=small, alignment=TA_CENTER)
    small_b = ParagraphStyle("small_b", parent=small,
                             fontName="Helvetica-Bold",
                             textColor=colors.white)
    h1 = ParagraphStyle("h1", parent=ss["Title"], fontName="Helvetica-Bold",
                        fontSize=20, leading=24, textColor=NAVY,
                        alignment=TA_LEFT, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=body, textColor=colors.grey,
                         spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"],
                        fontName="Helvetica-Bold", fontSize=13.5,
                        textColor=NAVY, spaceBefore=12, spaceAfter=6)
    h3 = ParagraphStyle("h3", parent=body, fontName="Helvetica-Bold",
                        spaceBefore=4, spaceAfter=2)
    bullet = ParagraphStyle("bullet", parent=body, leftIndent=14,
                            bulletIndent=2, spaceAfter=3)
    bullet_s = ParagraphStyle("bullet_s", parent=bullet, fontSize=9,
                              leading=12)

    def bullets(items, numbered=False, style=bullet):
        return [Paragraph(t, style, bulletText=f"{i}." if numbered
                          else "•")
                for i, t in enumerate(items, 1)]

    def header_row(cells):
        return [Paragraph(x, small_b) for x in cells]

    def grid_style(extra=()):
        return TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY),
                           ("GRID", (0, 0), (-1, -1), 0.5, GRID),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                           *extra])

    def tag_color(tag):
        if tag.startswith(A):
            return TAG_A
        if tag.startswith(B):
            return TAG_B
        return TAG_DECIDE if tag.lower().startswith("decide") else TAG_MIXED

    story = [Paragraph(c["title"], h1), Paragraph(c["subtitle"], sub),
             Paragraph("What we compared", h2), Paragraph(c["intro"], body)]

    verdict = Table([[bullets(c["verdict"])]], colWidths=[6.5 * inch])
    verdict.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CALLOUT_FILL),
        ("BOX", (0, 0), (-1, -1), 0.6, CALLOUT_EDGE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story += [Paragraph("The verdict", h2), verdict,
              Paragraph("What is the same", h2)]
    story += bullets(c["same"])

    shade = {A: SIDE_A_FILL, B: SIDE_B_FILL, "Tie": TIE_FILL}
    rows = [header_row(["Area", A, B, "Better", "Why"])]
    extra = [("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for i, (area, a, b, why) in enumerate(c["scores"], 1):
        w = better(a, b, c)
        rows.append([Paragraph(area, small), Paragraph(str(a), small_c),
                     Paragraph(str(b), small_c), Paragraph(w, small_c),
                     Paragraph(why, small)])
        extra.append(("BACKGROUND", (3, i), (3, i), shade[w]))
    ta, tb = averages(c)
    last = len(rows)
    rows.append([Paragraph("<b>Average</b>", small),
                 Paragraph(f"<b>{ta:.1f}</b>", small_c),
                 Paragraph(f"<b>{tb:.1f}</b>", small_c),
                 Paragraph(f"<b>{better(ta, tb, c)}</b>", small_c),
                 Paragraph(c.get("average_note", ""), small)])
    extra += [("BACKGROUND", (0, last), (2, last), TIE_FILL),
              ("BACKGROUND", (3, last), (3, last), shade[better(ta, tb, c)]),
              ("BACKGROUND", (4, last), (4, last), TIE_FILL)]
    sc = Table(rows, colWidths=[2.25 * inch, 0.5 * inch, 0.5 * inch,
                                0.6 * inch, 2.65 * inch], repeatRows=1)
    sc.setStyle(grid_style(extra))
    story.append(KeepTogether([
        Paragraph("Senior developer's scorecard "
                  "<font size=10 color='#666666'>(1 = poor, 5 = excellent)"
                  "</font>", h2), sc]))

    story.append(Paragraph("The main differences, in plain words", h2))
    for head, tag, text in c["differences"]:
        story.append(KeepTogether([
            Paragraph(f"{head} &nbsp;<font color='{tag_color(tag)}' "
                      f"size=9>[{tag}]</font>", h3),
            Paragraph(text, body), Spacer(1, 4)]))

    so = c.get("sample_output")
    if so:
        n = len(so["columns"])
        t = Table([header_row(so["columns"])] +
                  [[Paragraph(x, small) for x in r] for r in so["rows"]],
                  colWidths=[6.5 * inch / n] * n, repeatRows=1)
        t.setStyle(grid_style())
        story += [Paragraph("Sample output comparison", h2),
                  Paragraph(so["intro"], body), Spacer(1, 6), t]

    if c.get("shared"):
        story.append(Paragraph("Problems both versions share", h2))
        story += bullets(c["shared"])

    fix = Table([header_row([A, B]),
                 [bullets(c["fix_a"], style=bullet_s),
                  bullets(c["fix_b"], style=bullet_s)]],
                colWidths=[3.25 * inch, 3.25 * inch])
    fix.setStyle(grid_style([("BACKGROUND", (0, 1), (0, 1), SIDE_A_FILL),
                             ("BACKGROUND", (1, 1), (1, 1), SIDE_B_FILL),
                             ("TOPPADDING", (0, 0), (-1, -1), 5)]))
    story.append(KeepTogether([
        Paragraph("Production sign-off: what must change first", h2),
        Paragraph(c.get("fix_intro", ""), body), Spacer(1, 6), fix]))

    if c.get("housekeeping"):
        story.append(Paragraph("Housekeeping", h2))
        story += bullets(c["housekeeping"])

    story.append(Paragraph("Recommended next steps", h2))
    story += bullets(c["next_steps"], numbered=True)

    gl = [header_row(["Term", "Meaning"])]
    gl += [[Paragraph(f"<b>{t}</b>", small), Paragraph(d, small)]
           for t, d in c["glossary"]]
    g = Table(gl, colWidths=[1.5 * inch, 5.0 * inch])
    g.setStyle(grid_style())
    story.append(KeepTogether([Paragraph("Glossary", h2), g]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(0.75 * inch, 0.5 * inch, c["footer"])
        canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(path), pagesize=letter,
                            leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.8 * inch,
                            title=c["title"], author="Comparison review")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    content = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out = Path(sys.argv[2])
    write_markdown(content, out / f"{content['output_name']}.md")
    write_pdf(content, out / f"{content['output_name']}.pdf")
    print(f"wrote {content['output_name']}.md and .pdf")
