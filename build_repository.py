from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CHECKLISTS = {
    "routine": {
        "name": "Routine or recurring clean",
        "description": "Maintenance cleaning for a home that is already in generally good condition.",
    },
    "deep": {
        "name": "Deep clean",
        "description": "A more detailed reset for visible buildup, first visits, or seasonal cleaning.",
    },
    "move": {
        "name": "Move-in or move-out clean",
        "description": "An empty-home reset. Interior storage and appliances must be emptied first.",
    },
}

TASK_GROUPS = [
    ("Kitchen", [
        ("Counters, backsplash, sink, and faucet", "included", "included", "included", ""),
        ("Microwave inside and outside", "included", "included", "included", ""),
        ("Appliance exteriors", "included", "included", "included", ""),
        ("Cabinet and drawer fronts", "not_included", "included", "included", ""),
        ("Inside empty cabinets and drawers", "not_included", "optional", "included", "Empty first."),
        ("Inside refrigerator", "optional", "optional", "included", "Empty first for move cleaning."),
        ("Inside oven", "optional", "optional", "included", "Normal-use buildup only."),
        ("Range hood exterior", "not_included", "included", "included", ""),
        ("Range hood interior or filter detail", "optional", "optional", "optional", "Confirm before service."),
    ]),
    ("Bathrooms", [
        ("Toilets, base, and behind", "included", "included", "included", ""),
        ("Tub, shower, sink, faucet, counters, and mirrors", "included", "included", "included", ""),
        ("Surface scrub of accessible tile and grout", "not_included", "included", "included", "Permanent stains may remain."),
        ("Hard-water buildup or heavy soap scum", "optional", "included", "included", "Cleaning cannot reverse permanent staining or damage."),
        ("Mold, biohazard, urine, feces, or animal waste", "not_included", "not_included", "not_included", "Use an appropriate specialist."),
    ]),
    ("Living areas and bedrooms", [
        ("Dust reachable surfaces, lamps, frames, and sills", "included", "included", "included", ""),
        ("Vacuum, sweep, mop, and empty trash", "included", "included", "included", ""),
        ("Make beds when fresh linens are left out", "included", "included", "not_included", ""),
        ("Baseboards", "not_included", "included", "included", ""),
        ("Door frames", "not_included", "included", "included", ""),
        ("Reachable fans and fixtures", "not_included", "included", "included", "Use a two-step ladder at most."),
        ("Move light furniture", "not_included", "optional", "optional", "Do not move heavy furniture, appliances, or large rugs."),
        ("Heavy pet hair", "optional", "optional", "optional", "Pet waste is not included."),
    ]),
    ("Windows and utility areas", [
        ("Up to 10 reachable interior windows", "not_included", "included", "included", "Interior glass only."),
        ("Window tracks and blinds", "optional", "optional", "optional", "Confirm before service."),
        ("Inside empty closets", "not_included", "optional", "included", "Empty first."),
        ("Garage or basement sweeping", "not_included", "optional", "optional", "Only when specifically quoted. No hauling or organizing."),
        ("Laundry and folding", "optional", "optional", "optional", "Machine cycles affect how much can be completed."),
        ("Light wall spot-cleaning", "optional", "included", "included", "Small safe wipes only. Permanent marks may remain."),
        ("Full wall washing", "not_included", "not_included", "not_included", "May damage paint. Use an appropriate specialist."),
    ]),
]

DIRT_CODE = [
    (1, "Immaculate", "Pristine throughout. Light maintenance only.", "maintained"),
    (2, "Exceptional", "Cleaned almost daily. A quick refresh.", "maintained"),
    (3, "Good", "Light surface dust. Looks weekly-cleaned.", "maintained"),
    (4, "Maintained", "Light buildup. Looks biweekly-cleaned.", "maintained"),
    (5, "Average", "Comfortably lived in. Light soap scum. A deep clean may fit better.", "review_fit"),
    (6, "Moderate", "Pets or kids. Moderate bathroom or kitchen buildup.", "photos_required"),
    (7, "Fallen Behind", "Noticeable buildup in bathrooms and kitchen.", "photos_required"),
    (8, "Challenging", "Heavy dust, soap scum, or kitchen buildup. Detailed scrubbing is needed.", "photos_required"),
    (9, "Maximum Challenge", "Intensive detailing throughout. Some floors may need multiple passes.", "photos_required"),
    (10, "Specialist", "Biohazard, hoarding, pest waste, or unsafe conditions require a qualified specialist.", "specialist"),
]


def rows():
    output = []
    for area, tasks in TASK_GROUPS:
        for task, routine, deep, move, note in tasks:
            output.append({
                "area": area,
                "task": task,
                "routine": routine,
                "deep": deep,
                "move_in_out": move,
                "notes": note,
            })
    return output


def write_text_files():
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "checklists").mkdir(exist_ok=True)
    (ROOT / "templates").mkdir(exist_ok=True)
    (ROOT / "printables").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    all_rows = rows()
    payload = {
        "version": "1.0.0",
        "license": "CC-BY-4.0",
        "source": "https://www.shinygoclean.com/checklist",
        "status_values": {
            "included": "Included in the selected clean",
            "optional": "Optional add-on or custom-scope item",
            "not_included": "Not included in the selected clean",
        },
        "services": CHECKLISTS,
        "tasks": all_rows,
        "dirt_code": [
            {"score": score, "label": label, "description": description, "booking_guidance": guidance}
            for score, label, description, guidance in DIRT_CODE
        ],
    }
    (ROOT / "data" / "cleaning-checklists.json").write_text(json.dumps(payload, indent=2) + "\n")
    with (ROOT / "data" / "cleaning-checklists.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["area", "task", "routine", "deep", "move_in_out", "notes"])
        writer.writeheader()
        writer.writerows(all_rows)
    with (ROOT / "data" / "dirt-code.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["score", "label", "description", "booking_guidance"])
        writer.writerows(DIRT_CODE)
    for key, service in CHECKLISTS.items():
        path = ROOT / "checklists" / f"{key.replace('_', '-')}.md"
        lines = [f"# {service['name']}", "", service["description"], ""]
        for area, tasks in TASK_GROUPS:
            lines.extend([f"## {area}", ""])
            for task, routine, deep, move, note in tasks:
                status = {"routine": routine, "deep": deep, "move": move}[key]
                marker = "x" if status == "included" else " "
                suffix = ""
                if status == "optional":
                    suffix = " (optional or custom scope)"
                elif status == "not_included":
                    suffix = " (not included)"
                if note:
                    suffix += f" - {note}"
                lines.append(f"- [{marker}] {task}{suffix}")
            lines.append("")
        path.write_text("\n".join(lines))
    with (ROOT / "templates" / "blank-cleaning-checklist.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["area", "task", "included", "optional_add_on", "not_included", "notes"])
        for _ in range(20):
            writer.writerow(["", "", "", "", "", ""])


def build_pdfs():
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase import pdfmetrics
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether

    blue = colors.HexColor("#336AE3")
    navy = colors.HexColor("#122A49")
    pale = colors.HexColor("#EEF4FF")
    green = colors.HexColor("#DCEAD5")
    amber = colors.HexColor("#F5E8C8")
    coral = colors.HexColor("#F6DDD1")
    rose = colors.HexColor("#EBD9DF")
    gray = colors.HexColor("#62718A")
    white = colors.white

    body = ParagraphStyle("body", fontName="Helvetica", fontSize=6.4, leading=7.4, textColor=navy)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=5.4, leading=6.2, textColor=gray)
    header = ParagraphStyle("header", fontName="Helvetica-Bold", fontSize=6.6, leading=7.2, textColor=white, alignment=TA_CENTER)
    section = ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=6.3, leading=7, textColor=navy)

    checklist_path = ROOT / "printables" / "shiny-go-clean-one-page-checklist.pdf"
    doc = SimpleDocTemplate(str(checklist_path), pagesize=landscape(letter), leftMargin=0.27*inch, rightMargin=0.27*inch, topMargin=0.2*inch, bottomMargin=0.22*inch)
    story = []
    title_table = Table([
        [Paragraph("<b>Shiny Go Clean</b><br/><font size='6'>Madison, Wisconsin</font>", ParagraphStyle("brand", parent=body, fontSize=9, leading=10, textColor=navy)),
         Paragraph("<b>Residential Cleaning Checklist</b><br/><font size='6'>A one-page scope template for routine, deep, and move-in or move-out cleaning</font>", ParagraphStyle("title", parent=body, fontSize=15, leading=16, alignment=TA_CENTER, textColor=blue)),
         Paragraph("<b>Home:</b> __________________<br/><b>Date:</b> __________________<br/><b>Cleaner:</b> ________________", ParagraphStyle("fields", parent=small, alignment=TA_LEFT))]
    ], colWidths=[1.45*inch, 6.15*inch, 2.7*inch])
    title_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    story.append(title_table)
    status_symbol = {"included": "YES", "optional": "OPT", "not_included": "NO"}
    table_data = [[Paragraph("Area", header), Paragraph("Task", header), Paragraph("Routine", header), Paragraph("Deep", header), Paragraph("Move", header), Paragraph("Notes", header)]]
    group_starts = []
    for area, tasks in TASK_GROUPS:
        group_starts.append(len(table_data))
        for index, (task, routine, deep, move, note) in enumerate(tasks):
            table_data.append([
                Paragraph(area if index == 0 else "", section),
                Paragraph(task, body),
                Paragraph(status_symbol[routine], ParagraphStyle("c1", parent=small, alignment=TA_CENTER, textColor=navy)),
                Paragraph(status_symbol[deep], ParagraphStyle("c2", parent=small, alignment=TA_CENTER, textColor=navy)),
                Paragraph(status_symbol[move], ParagraphStyle("c3", parent=small, alignment=TA_CENTER, textColor=navy)),
                Paragraph(note, small),
            ])
    table = Table(table_data, colWidths=[0.96*inch, 3.25*inch, 0.57*inch, 0.57*inch, 0.57*inch, 4.38*inch], repeatRows=1, rowHeights=[0.23*inch] + [0.178*inch]*(len(table_data)-1))
    style = [
        ("BACKGROUND", (0,0), (-1,0), blue), ("GRID", (0,0), (-1,-1), 0.35, colors.HexColor("#B8CDF7")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
        ("TOPPADDING", (0,0), (-1,-1), 1), ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("BACKGROUND", (0,1), (-1,-1), white),
    ]
    for start in group_starts:
        style.extend([("BACKGROUND", (0,start), (0,start + len(TASK_GROUPS[group_starts.index(start)][1]) - 1), pale), ("LINEABOVE", (0,start), (-1,start), 1.1, blue)])
    for row_index, row in enumerate(rows(), start=1):
        for col_index, key in ((2, "routine"), (3, "deep"), (4, "move_in_out")):
            fill = {"included": green, "optional": amber, "not_included": colors.HexColor("#F1F3F6")}[row[key]]
            style.append(("BACKGROUND", (col_index,row_index), (col_index,row_index), fill))
    table.setStyle(TableStyle(style))
    story.append(table)
    legend = Table([[
        Paragraph("<b>YES</b> included", small), Paragraph("<b>OPT</b> optional or custom scope", small), Paragraph("<b>NO</b> not included", small),
        Paragraph("Always confirm access, priorities, add-ons, safety limits, and the final scope before service.", small),
        Paragraph("Source: <link href='https://www.shinygoclean.com/checklist' color='#336AE3'>shinygoclean.com/checklist</link>", small),
    ]], colWidths=[0.8*inch, 1.45*inch, 1.05*inch, 4.6*inch, 2.4*inch])
    legend.setStyle(TableStyle([("TOPPADDING", (0,0), (-1,-1), 4), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.append(legend)
    doc.build(story)

    dirt_path = ROOT / "printables" / "dirt-code-condition-guide.pdf"
    doc = SimpleDocTemplate(str(dirt_path), pagesize=landscape(letter), leftMargin=0.42*inch, rightMargin=0.42*inch, topMargin=0.35*inch, bottomMargin=0.35*inch)
    story = [Paragraph("<font color='#336AE3'>HOW TO DESCRIBE A HOME'S CONDITION</font>", ParagraphStyle("eyebrow", parent=small, fontName="Helvetica-Bold", fontSize=7, leading=8, spaceAfter=3)),
             Paragraph("Dirt Code <font color='#336AE3'><i>Guide</i></font>", ParagraphStyle("dtitle", parent=body, fontName="Helvetica-Bold", fontSize=27, leading=29, textColor=navy)),
             Paragraph("A simple 1-10 condition score for discussing scope before cleaning begins.", ParagraphStyle("dsub", parent=body, fontSize=9, leading=11, textColor=gray, spaceAfter=8))]
    groups = [("Maintained", DIRT_CODE[0:4], green), ("Review fit", DIRT_CODE[4:5], amber), ("Photos required", DIRT_CODE[5:9], coral), ("Specialist", DIRT_CODE[9:10], rose)]
    columns = []
    for group_name, items, tint in groups:
        group_flow = [Paragraph(f"<b>{group_name.upper()}</b>", ParagraphStyle("gh", parent=small, fontSize=7, leading=8, textColor=navy, spaceAfter=3))]
        for score, label, description, guidance in items:
            card = Table([[Paragraph(str(score), ParagraphStyle("score", parent=body, fontName="Helvetica-Bold", fontSize=17, leading=18, alignment=TA_CENTER, textColor=navy)),
                           Paragraph(f"<b>{label}</b><br/><font color='#62718A'>{description}</font>", ParagraphStyle("card", parent=body, fontSize=8, leading=9.4))]], colWidths=[0.58*inch, 1.96*inch])
            card.setStyle(TableStyle([("BACKGROUND", (0,0), (0,0), tint), ("BOX", (0,0), (-1,-1), 0.4, colors.HexColor("#D9DEE8")), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
            group_flow.extend([card, Spacer(1, 4)])
        columns.append(group_flow)
    outer = Table([columns], colWidths=[2.66*inch, 2.66*inch, 2.66*inch, 2.66*inch])
    outer.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5)]))
    story.append(outer)
    story.append(Spacer(1, 8))
    guidance = Table([[
        Paragraph("<b>Booking guidance</b><br/>Scores 1-4 are maintained or light. Score 5 may need a deep clean. Scores 6-9 require photos before booking so the scope can be confirmed. Score 10 requires an appropriate specialist.", ParagraphStyle("guide", parent=body, fontSize=7.5, leading=9)),
        Paragraph("Created by <link href='https://www.shinygoclean.com/' color='#336AE3'><b>Shiny Go Clean</b></link><br/>Madison, Wisconsin<br/>(608) 292-6848", ParagraphStyle("contact", parent=body, fontSize=7.5, leading=9, alignment=TA_LEFT)),
    ]], colWidths=[7.8*inch, 2.8*inch])
    guidance.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), pale), ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#B8CDF7")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("PADDING", (0,0), (-1,-1), 7)]))
    story.append(guidance)
    doc.build(story)


def publish_docs_downloads():
    downloads = ROOT / "docs" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    for source in (
        ROOT / "printables" / "shiny-go-clean-one-page-checklist.pdf",
        ROOT / "printables" / "dirt-code-condition-guide.pdf",
        ROOT / "data" / "cleaning-checklists.csv",
        ROOT / "data" / "cleaning-checklists.json",
        ROOT / "templates" / "blank-cleaning-checklist.csv",
    ):
        shutil.copy2(source, downloads / source.name)


def main():
    write_text_files()
    build_pdfs()
    publish_docs_downloads()
    print(f"generated {len(rows())} task rows and {len(DIRT_CODE)} Dirt Code rows")


if __name__ == "__main__":
    main()
