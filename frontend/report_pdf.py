"""Clinical Report PDF — matches screenshot 5. © 2026 Lamya F. H. Ali"""
import os
from datetime import datetime


def build_report(child, summary, parent_notes=None, pecs_log=None, skills=None):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    name=child.get("name","child")
    path=os.path.join(os.path.expanduser("~"), f"Pepper_Report_{name}.pdf")
    doc=SimpleDocTemplate(path, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles=getSampleStyleSheet()
    H=ParagraphStyle("H", parent=styles["Title"], fontSize=20, spaceAfter=14)
    SH=ParagraphStyle("SH", parent=styles["Heading2"], fontSize=14, spaceBefore=14, spaceAfter=6)
    P=styles["Normal"]; small=ParagraphStyle("sm",parent=P,fontSize=9)
    el=[]

    el.append(Paragraph(f"Clinical Report — {name}", H))

    skills=skills or {}
    rows=[
        ["Item","Value"],
        ["Child", name],
        ["Age", str(child.get("age",""))],
        ["Date", datetime.now().strftime("%Y-%m-%d")],
        ["Duration", f"{summary.get('duration_sec',0)//60} min"],
        ["Score", str(summary.get("score",0))],
        ["Mastered", str(summary.get("mastered",0))],
        ["OK", str(summary.get("ok",0))],
        ["Fail", str(summary.get("fail",0))],
        ["Skip", str(summary.get("skip",0))],
        ["Motor", f"{int(skills.get('Motor',0))}%"],
        ["Cognitive", f"{int(skills.get('Cognitive',0))}%"],
        ["Verbal", f"{int(skills.get('Verbal',0))}%"],
        ["Math", f"{int(skills.get('Math',0))}%"],
        ["Social", f"{int(skills.get('Social',0))}%"],
        ["Avg Attention", f"{summary.get('avg_attention',0)}%"],
        ["Dominant Mood", summary.get("dominant_emotion","neutral")],
    ]
    t=Table(rows, colWidths=[6*cm,9*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4f46e5")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),11),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f8fafc")]),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),10),
    ]))
    el.append(t)

    if parent_notes:
        el.append(Paragraph("Parent Notes", SH))
        for n in parent_notes:
            el.append(Paragraph(n, small))

    if pecs_log:
        el.append(Paragraph("PECS Log", SH))
        for p in pecs_log:
            el.append(Paragraph(p, small))

    el.append(Spacer(1,18))
    el.append(Paragraph(
        "© 2026 Lamya Fadlulmola Hamed Ali — Pepper Clinical Infinity V6 — All Rights Reserved",
        ParagraphStyle("cr",parent=small,textColor=colors.HexColor("#94a3b8"),fontSize=8)))
    doc.build(el)
    return path
