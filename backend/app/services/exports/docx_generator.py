import os
import datetime
from typing import Dict, Any, List
# pyrefly: ignore [missing-import]
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from app.config import settings

def generate_docx_report(
    form_id: str,
    form_title: str,
    form_description: str,
    stats: Dict[str, Any],
    text_analysis: Dict[str, Any],
    comparisons: List[Dict[str, Any]],
    ai_insights: Dict[str, Any]
) -> str:
    """
    Generates a professionally styled Microsoft Word (.docx) document report.
    """
    filename = f"FormMind_Report_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    doc = Document()

    # Document Title
    title_p = doc.add_paragraph()
    title_run = title_p.add_run(f"FormMind AI — Analysis Report\n{form_title}")
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(234, 88, 12) # Peach Coral
    title_p.paragraph_format.space_after = Pt(4)

    # Subtitle / Date
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    sub_p = doc.add_paragraph(f"Report Generated: {date_str} | Verified Analytical Intelligence")
    sub_p.paragraph_format.space_after = Pt(16)

    # KPI Table
    basic = stats.get("basic", {})
    overview = stats.get("overview_cards", {})
    
    kpi_table = doc.add_table(rows=2, cols=4)
    kpi_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Total Responses", "Completion Rate", "Average Rating", "Questions"]
    values = [
        str(basic.get("total_responses", 0)),
        str(basic.get("completion_rate", "100%")),
        str(overview.get("average_rating", "N/A")),
        str(basic.get("total_questions", 0))
    ]
    for i in range(4):
        h_cell = kpi_table.cell(0, i)
        h_cell.text = headers[i]
        h_cell.paragraphs[0].runs[0].font.bold = True
        v_cell = kpi_table.cell(1, i)
        v_cell.text = values[i]
        v_cell.paragraphs[0].runs[0].font.size = Pt(14)
        v_cell.paragraphs[0].runs[0].font.bold = True
        v_cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(234, 88, 12)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 1. Executive Summary
    h1 = doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(ai_insights.get("executive_summary", "Detailed survey analytics report."))

    # 2. Key Findings & Insights
    doc.add_heading("2. Grounded AI Insights & Findings", level=1)
    if ai_insights.get("facts"):
        doc.add_heading("Calculated Ground-Truth Facts", level=2)
        for f in ai_insights["facts"][:6]:
            doc.add_paragraph(f, style='List Bullet')
            
    if ai_insights.get("interpretations"):
        doc.add_heading("Data Interpretations", level=2)
        for item in ai_insights["interpretations"][:4]:
            doc.add_paragraph(item, style='List Bullet')

    if ai_insights.get("recommendations"):
        doc.add_heading("Actionable Recommendations", level=2)
        for r in ai_insights["recommendations"][:4]:
            doc.add_paragraph(r, style='List Bullet')

    # 3. Question-by-Question Breakdown
    doc.add_heading("3. Question-by-Question Breakdown", level=1)

    numerical = stats.get("numerical", {})
    for k, num in numerical.items():
        doc.add_heading(f"{num.get('question_text')} (Numerical Rating)", level=2)
        doc.add_paragraph(f"Responses: {num.get('count')} | Mean: {num.get('mean')} | Median: {num.get('median')} | Std Dev: {num.get('std_dev')} | Min: {num.get('min')} | Max: {num.get('max')}")
        
        dist = num.get("distribution", [])
        if dist:
            t = doc.add_table(rows=1 + len(dist), cols=3)
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.cell(0, 0).text = "Score / Bucket"
            t.cell(0, 1).text = "Count"
            t.cell(0, 2).text = "Percentage"
            for r_idx, d in enumerate(dist):
                t.cell(r_idx + 1, 0).text = str(d.get("label"))
                t.cell(r_idx + 1, 1).text = str(d.get("count"))
                t.cell(r_idx + 1, 2).text = f"{d.get('percentage')}%"
        doc.add_paragraph()

    categorical = stats.get("categorical", {})
    for k, cat in categorical.items():
        doc.add_heading(f"{cat.get('question_text')} (Multiple Choice)", level=2)
        doc.add_paragraph(f"Total Answers: {cat.get('count')} | Unique Options: {cat.get('unique_count')}")
        dist = cat.get("distribution", [])
        if dist:
            t = doc.add_table(rows=1 + len(dist), cols=3)
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.cell(0, 0).text = "Option"
            t.cell(0, 1).text = "Responses"
            t.cell(0, 2).text = "Percentage"
            for r_idx, d in enumerate(dist):
                t.cell(r_idx + 1, 0).text = str(d.get("label"))
                t.cell(r_idx + 1, 1).text = str(d.get("count"))
                t.cell(r_idx + 1, 2).text = f"{d.get('percentage')}%"
        doc.add_paragraph()

    # 4. Comparative Analysis
    if comparisons:
        doc.add_heading("4. Comparative Segment Analysis", level=1)
        for comp in comparisons:
            doc.add_heading(comp.get("title"), level=2)
            doc.add_paragraph(comp.get("key_insight"))
            segs = comp.get("segments", [])
            if segs:
                t = doc.add_table(rows=1 + len(segs), cols=4)
                t.alignment = WD_TABLE_ALIGNMENT.CENTER
                t.cell(0, 0).text = "Segment Group"
                t.cell(0, 1).text = "Count"
                t.cell(0, 2).text = "Mean Score"
                t.cell(0, 3).text = "Median"
                for r_idx, s in enumerate(segs):
                    t.cell(r_idx + 1, 0).text = str(s.get("group"))
                    t.cell(r_idx + 1, 1).text = str(s.get("count"))
                    t.cell(r_idx + 1, 2).text = str(s.get("mean"))
                    t.cell(r_idx + 1, 3).text = str(s.get("median"))
            doc.add_paragraph()

    # 5. Open-Ended Feedback Highlights
    if text_analysis:
        doc.add_heading("5. Open-Ended Feedback & Sentiment Highlights", level=1)
        for k, txt in text_analysis.items():
            doc.add_heading(txt.get("question_text"), level=2)
            s = txt.get("sentiment", {})
            doc.add_paragraph(f"Sentiment: {s.get('positive_percentage')}% Positive | {s.get('negative_percentage')}% Negative (Score: {s.get('score')})")
            if txt.get("positive_feedback"):
                doc.add_paragraph("Top Positive Feedback:")
                for p in txt["positive_feedback"][:3]:
                    doc.add_paragraph(f"\"{p}\"", style='List Bullet')
            if txt.get("negative_feedback"):
                doc.add_paragraph("Constructive Critiques / Complaints:")
                for n in txt["negative_feedback"][:3]:
                    doc.add_paragraph(f"\"{n}\"", style='List Bullet')

    doc.save(file_path)
    return file_path
