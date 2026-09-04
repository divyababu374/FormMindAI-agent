import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend root is in sys.path so 'app' can be imported when running directly or in different working directories
_backend_dir = str(Path(__file__).resolve().parents[3])
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

# pyrefly: ignore [missing-import]
from docx import Document  # type: ignore
# pyrefly: ignore [missing-import]
from docx.shared import Inches, Pt, RGBColor  # type: ignore
# pyrefly: ignore [missing-import]
from docx.enum.text import WD_ALIGN_PARAGRAPH  # type: ignore
# pyrefly: ignore [missing-import]
from docx.enum.table import WD_TABLE_ALIGNMENT  # type: ignore

try:
    from app.config import settings
except ImportError:
    class _FallbackSettings:
        EXPORTS_DIR = os.path.join(_backend_dir, "exports")
    settings = _FallbackSettings()  # type: ignore

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
    os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
    filename = f"FormMind_Report_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    doc = Document()

    # Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
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


if __name__ == "__main__":
    print("Testing DOCX Report Generator...")
    sample_stats = {
        "basic": {
            "total_responses": 42,
            "completion_rate": "98%",
            "total_questions": 5
        },
        "overview_cards": {
            "average_rating": 4.6
        },
        "numerical": {
            "q1": {
                "question_text": "Overall Satisfaction",
                "count": 42,
                "mean": 4.6,
                "median": 5.0,
                "std_dev": 0.5,
                "min": 3,
                "max": 5,
                "distribution": [
                    {"label": "5 Stars", "count": 28, "percentage": 66.7},
                    {"label": "4 Stars", "count": 12, "percentage": 28.6},
                    {"label": "3 Stars", "count": 2, "percentage": 4.8}
                ]
            }
        },
        "categorical": {
            "q2": {
                "question_text": "Department",
                "count": 42,
                "unique_count": 3,
                "distribution": [
                    {"label": "Engineering", "count": 20, "percentage": 47.6},
                    {"label": "Product", "count": 14, "percentage": 33.3},
                    {"label": "Design", "count": 8, "percentage": 19.0}
                ]
            }
        }
    }
    sample_text_analysis = {
        "q3": {
            "question_text": "Any suggestions for improvement?",
            "sentiment": {
                "positive_percentage": 85,
                "negative_percentage": 15,
                "score": 0.72
            },
            "positive_feedback": [
                "Great user interface and speed!",
                "The AI insights saved our team hours of manual analysis."
            ],
            "negative_feedback": [
                "Would love to see more export formats."
            ]
        }
    }
    sample_comparisons = [
        {
            "title": "Satisfaction by Department",
            "key_insight": "Engineering reported slightly higher satisfaction than other teams.",
            "segments": [
                {"group": "Engineering", "count": 20, "mean": 4.8, "median": 5.0},
                {"group": "Product", "count": 14, "mean": 4.5, "median": 4.5},
                {"group": "Design", "count": 8, "mean": 4.3, "median": 4.0}
            ]
        }
    ]
    sample_ai = {
        "executive_summary": "The survey indicates overwhelmingly positive sentiment across all departments, with strong praise for interface responsiveness.",
        "facts": [
            "Total of 42 responses collected with 98% completion rate.",
            "Overall satisfaction average stands at 4.6 out of 5."
        ],
        "interpretations": [
            "Team members value analytical automation highly."
        ],
        "recommendations": [
            "Expand export capabilities to include PowerPoint presentations."
        ]
    }

    output_path = generate_docx_report(
        form_id="demo_sample_123",
        form_title="Quarterly Product Feedback",
        form_description="Comprehensive employee & customer feedback analysis",
        stats=sample_stats,
        text_analysis=sample_text_analysis,
        comparisons=sample_comparisons,
        ai_insights=sample_ai
    )
    try:
        print(f"SUCCESS: DOCX report successfully generated at:\n{output_path}")
    except UnicodeEncodeError:
        print(f"SUCCESS: DOCX report successfully generated at:\n{output_path.encode('ascii', errors='replace').decode('ascii')}")
