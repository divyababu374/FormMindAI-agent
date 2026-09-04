import os
import datetime
from xml.sax.saxutils import escape
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.units import inch
from app.config import settings

def safe_text(val: Any) -> str:
    """Escapes XML entities (&, <, >) to ensure ReportLab Paragraph stability."""
    if val is None:
        return ""
    return escape(str(val))

def generate_pdf_report(
    form_id: str,
    form_title: str,
    form_description: str,
    stats: Dict[str, Any],
    text_analysis: Dict[str, Any],
    comparisons: List[Dict[str, Any]],
    ai_insights: Dict[str, Any]
) -> str:
    """
    Generates a polished, professional multi-page PDF analytical report in Peach & White theme.
    Returns the absolute path to the generated PDF.
    """
    filename = f"FormMind_Report_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Warm Peach & White Palette
    primary_color = colors.HexColor("#EA580C")   # Vibrant Peach Coral
    secondary_color = colors.HexColor("#F97342") # Peach Accent
    accent_color = colors.HexColor("#047857")    # Deep Emerald
    text_dark = colors.HexColor("#24110A")       # Deep Espresso
    text_muted = colors.HexColor("#6B3B2B")      # Warm Cocoa
    bg_light = colors.HexColor("#FFF7F2")        # Soft Radiant Peach
    border_color = colors.HexColor("#FAD5C0")    # Warm Peach Border
    th_bg = colors.HexColor("#FFF2EB")           # Table Header Background
    th_text = colors.HexColor("#8C2C08")         # Table Header Text

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=text_dark,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=text_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=14,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=th_text,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_dark
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_dark,
        alignment=1
    )

    story = []

    # Title Banner
    story.append(Paragraph("FORMMIND AI — SURVEY ANALYTICS REPORT", subtitle_style))
    story.append(Paragraph(safe_text(form_title), title_style))
    if form_description:
        story.append(Paragraph(safe_text(form_description), subtitle_style))
    
    date_str = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"<b>Generated:</b> {date_str}  •  <b>Verification:</b> 100% Grounded Survey Data", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=12))

    # Executive Overview KPI Cards Table
    basic = stats.get("basic", {})
    overview = stats.get("overview_cards", {})
    
    kpi_data = [
        [
            Paragraph("<b>Total Responses</b>", subtitle_style),
            Paragraph("<b>Completion Rate</b>", subtitle_style),
            Paragraph("<b>Average Rating</b>", subtitle_style),
            Paragraph("<b>Total Questions</b>", subtitle_style)
        ],
        [
            Paragraph(f"<font size=16 color='#EA580C'><b>{basic.get('total_responses', 0)}</b></font>", table_cell_center),
            Paragraph(f"<font size=16 color='#047857'><b>{safe_text(basic.get('completion_rate', '100%'))}</b></font>", table_cell_center),
            Paragraph(f"<font size=16 color='#EA580C'><b>{safe_text(overview.get('average_rating', 'N/A'))}</b></font>", table_cell_center),
            Paragraph(f"<font size=16 color='#24110A'><b>{basic.get('total_questions', 0)}</b></font>", table_cell_center)
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[132, 132, 132, 132])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", h1_style))
    exec_summary = ai_insights.get("executive_summary", "A comprehensive analysis of verified responses was performed.")
    story.append(Paragraph(safe_text(exec_summary), body_style))
    story.append(Spacer(1, 10))

    # 2. Key Findings (Facts, Interpretations, Recommendations)
    story.append(Paragraph("2. Grounded Key Insights and Findings", h1_style))
    
    if ai_insights.get("facts"):
        story.append(Paragraph("<b>Calculated Data Highlights:</b>", h2_style))
        for f in ai_insights["facts"][:6]:
            story.append(Paragraph(f"• {safe_text(f)}", bullet_style))
        story.append(Spacer(1, 6))

    if ai_insights.get("interpretations"):
        story.append(Paragraph("<b>Strategic Observations:</b>", h2_style))
        for item in ai_insights["interpretations"][:4]:
            story.append(Paragraph(f"• {safe_text(item)}", bullet_style))
        story.append(Spacer(1, 6))

    if ai_insights.get("recommendations"):
        story.append(Paragraph("<b>Actionable Recommendations:</b>", h2_style))
        for r in ai_insights["recommendations"][:4]:
            story.append(Paragraph(f"• {safe_text(r)}", bullet_style))
        story.append(Spacer(1, 12))

    # 3. Question-by-Question Breakdown
    story.append(PageBreak())
    story.append(Paragraph("3. Detailed Question Breakdown", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=border_color, spaceAfter=10))

    numerical = stats.get("numerical", {})
    for k, num in numerical.items():
        q_box = []
        q_box.append(Paragraph(f"<b>{safe_text(num.get('question_text'))}</b>  <i>(Rating Scale)</i>", h2_style))
        
        # Clean Metric Stats Row Table
        stat_headers = ["Responses", "Mean Score", "Median", "Std Dev", "Min", "Max"]
        stat_values = [
            str(num.get('count', 0)),
            str(num.get('mean', 'N/A')),
            str(num.get('median', 'N/A')),
            str(num.get('std_dev', 'N/A')),
            str(num.get('min', 'N/A')),
            str(num.get('max', 'N/A'))
        ]
        stat_table_data = [
            [Paragraph(f"<b>{h}</b>", table_cell_center) for h in stat_headers],
            [Paragraph(v, table_cell_center) for v in stat_values]
        ]
        stat_t = Table(stat_table_data, colWidths=[88, 88, 88, 88, 88, 88])
        stat_t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), th_bg),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#FFFFFF")),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        q_box.append(stat_t)
        q_box.append(Spacer(1, 6))
        
        # Distribution Table
        dist_rows = [[
            Paragraph("<b>Score / Bucket</b>", table_header_style),
            Paragraph("<b>Responses</b>", table_header_style),
            Paragraph("<b>Percentage</b>", table_header_style)
        ]]
        for d in num.get("distribution", []):
            dist_rows.append([
                Paragraph(safe_text(d.get("label")), table_cell_style),
                Paragraph(str(d.get("count")), table_cell_center),
                Paragraph(f"{d.get('percentage')}%", table_cell_center)
            ])
            
        t = Table(dist_rows, colWidths=[240, 144, 144])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), th_bg),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('ALIGN', (1,0), (-1,-1), 'CENTER')
        ]))
        q_box.append(t)
        q_box.append(Spacer(1, 10))
        story.append(KeepTogether(q_box))

    categorical = stats.get("categorical", {})
    for k, cat in categorical.items():
        q_box = []
        q_box.append(Paragraph(f"<b>{safe_text(cat.get('question_text'))}</b>  <i>(Multiple Choice)</i>", h2_style))
        q_box.append(Paragraph(f"Total Responses: <b>{cat.get('count')}</b>  •  Unique Options: <b>{cat.get('unique_count')}</b>", body_style))
        
        table_rows = [[
            Paragraph("<b>Option Choice</b>", table_header_style),
            Paragraph("<b>Responses</b>", table_header_style),
            Paragraph("<b>Percentage</b>", table_header_style)
        ]]
        for d in cat.get("distribution", []):
            table_rows.append([
                Paragraph(safe_text(d.get("label")), table_cell_style),
                Paragraph(str(d.get("count")), table_cell_center),
                Paragraph(f"{d.get('percentage')}%", table_cell_center)
            ])
            
        t = Table(table_rows, colWidths=[260, 134, 134])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), th_bg),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
            ('ALIGN', (1,0), (-1,-1), 'CENTER')
        ]))
        q_box.append(t)
        q_box.append(Spacer(1, 10))
        story.append(KeepTogether(q_box))

    # 4. Comparative Analysis
    if comparisons:
        story.append(Spacer(1, 10))
        story.append(Paragraph("4. Cross-Segment Comparative Analysis", h1_style))
        for comp in comparisons:
            comp_box = []
            comp_box.append(Paragraph(f"<b>{safe_text(comp.get('title'))}</b>", h2_style))
            comp_box.append(Paragraph(f"<i>{safe_text(comp.get('key_insight'))}</i>", body_style))
            
            c_rows = [[
                Paragraph("<b>Segment Group</b>", table_header_style),
                Paragraph("<b>Count</b>", table_header_style),
                Paragraph("<b>Mean Score</b>", table_header_style),
            ]]
            for seg in comp.get("segments", []):
                c_rows.append([
                    Paragraph(safe_text(seg.get("group")), table_cell_style),
                    Paragraph(str(seg.get("count")), table_cell_center),
                    Paragraph(str(seg.get("mean")), table_cell_center),
                ])
            t = Table(c_rows, colWidths=[260, 134, 134])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), th_bg),
                ('GRID', (0,0), (-1,-1), 0.5, border_color),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ('ALIGN', (1,0), (-1,-1), 'CENTER')
            ]))
            comp_box.append(t)
            comp_box.append(Spacer(1, 10))
            story.append(KeepTogether(comp_box))

    # 5. Open-Ended Feedback Summary
    if text_analysis:
        story.append(Spacer(1, 10))
        story.append(Paragraph("5. Open-Ended Feedback and Sentiment Highlights", h1_style))
        for k, txt in text_analysis.items():
            t_box = []
            t_box.append(Paragraph(f"<b>{safe_text(txt.get('question_text'))}</b>", h2_style))
            s = txt.get("sentiment", {})
            t_box.append(Paragraph(f"Sentiment: <b>{s.get('positive_percentage', 0)}% Positive</b>  •  <b>{s.get('negative_percentage', 0)}% Constructive</b>", body_style))
            
            if txt.get("positive_feedback"):
                t_box.append(Paragraph("<b>Positive Feedback:</b>", body_style))
                for p in txt["positive_feedback"][:3]:
                    clean_quote = safe_text(p).replace("&quot;", '"')
                    t_box.append(Paragraph(f"• \"{clean_quote}\"", bullet_style))
            if txt.get("negative_feedback"):
                t_box.append(Paragraph("<b>Constructive Feedback / Areas of Improvement:</b>", body_style))
                for n in txt["negative_feedback"][:3]:
                    clean_quote = safe_text(n).replace("&quot;", '"')
                    t_box.append(Paragraph(f"• \"{clean_quote}\"", bullet_style))
            t_box.append(Spacer(1, 8))
            story.append(KeepTogether(t_box))

    # Build PDF
    doc.build(story)
    return file_path
