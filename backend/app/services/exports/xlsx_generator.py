import os
import datetime
from typing import Dict, Any, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from app.config import settings

def sanitize_formula_cell(val: Any) -> Any:
    """
    Prevents Spreadsheet Formula Injection (CWE-1236).
    Escapes formula triggers (=, +, -, @, \t, \r) in text cells while preserving native numbers.
    """
    if val is None:
        return ""
    if isinstance(val, (int, float, bool)):
        return val
    s = str(val)
    if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + s
    return s

def generate_xlsx_workbook(
    form_id: str,
    form_title: str,
    questions: List[Dict[str, Any]],
    responses: List[Dict[str, Any]],
    stats: Dict[str, Any],
    ai_insights: Dict[str, Any]
) -> str:
    """
    Generates a 5-sheet comprehensive Excel workbook with formula-injection defenses.
    """
    filename = f"FormMind_Data_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    wb = openpyxl.Workbook()
    # Remove default sheet
    wb.remove(wb.active)

    # Styles
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    section_fill = PatternFill(start_color="EEF2FF", end_color="EEF2FF", fill_type="solid")
    section_font = Font(name="Arial", size=11, bold=True, color="1E3A8A")
    regular_font = Font(name="Arial", size=10)
    bold_font = Font(name="Arial", size=10, bold=True)
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # ----------------------------------------------------
    # Sheet 1: Summary
    # ----------------------------------------------------
    ws_summary = wb.create_sheet(title="Summary")
    ws_summary.append(["FormMind AI — Survey Analytics Summary"])
    ws_summary["A1"].font = Font(name="Arial", size=16, bold=True, color="1E3A8A")
    ws_summary.append([f"Form Title: {form_title}"])
    ws_summary.append([f"Generated Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
    ws_summary.append([])

    ws_summary.append(["Key Performance Indicators", "Value"])
    ws_summary["A5"].fill = header_fill
    ws_summary["A5"].font = header_font
    ws_summary["B5"].fill = header_fill
    ws_summary["B5"].font = header_font

    basic = stats.get("basic", {})
    overview = stats.get("overview_cards", {})
    ws_summary.append(["Total Responses", basic.get("total_responses", 0)])
    ws_summary.append(["Completion Rate", basic.get("completion_rate", "100%")])
    ws_summary.append(["Average Rating", overview.get("average_rating", "N/A")])
    ws_summary.append(["Total Questions", basic.get("total_questions", 0)])

    for row in range(5, 10):
        ws_summary[f"A{row}"].border = thin_border
        ws_summary[f"B{row}"].border = thin_border

    ws_summary.append([])
    ws_summary.append(["Executive Summary"])
    ws_summary["A11"].font = section_font
    ws_summary.append([ai_insights.get("executive_summary", "")])

    ws_summary.column_dimensions['A'].width = 30
    ws_summary.column_dimensions['B'].width = 50

    # ----------------------------------------------------
    # Sheet 2: Original Responses
    # ----------------------------------------------------
    ws_orig = wb.create_sheet(title="Original Responses")
    if responses:
        raw_headers = ["Response #", "Timestamp"]
        # Add question texts as headers
        for q in questions:
            raw_headers.append(q["question_text"])
        ws_orig.append(raw_headers)

        for col_num in range(1, len(raw_headers) + 1):
            cell = ws_orig.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border

        for r in responses:
            raw_data = r.get("raw_data", {})
            ts_str = str(r.get("submission_timestamp", ""))
            row_vals = [r.get("response_number", 1), ts_str]
            for q in questions:
                val = raw_data.get(q["question_text"])
                row_vals.append(sanitize_formula_cell(val))
            ws_orig.append(row_vals)

    # ----------------------------------------------------
    # Sheet 3: Cleaned Responses
    # ----------------------------------------------------
    ws_clean = wb.create_sheet(title="Cleaned Responses")
    if responses:
        clean_headers = ["Response #", "Timestamp"]
        for q in questions:
            clean_headers.append(f"{q['question_key']} ({q['question_text'][:30]}...)")
        ws_clean.append(clean_headers)

        for col_num in range(1, len(clean_headers) + 1):
            cell = ws_clean.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border

        for r in responses:
            cleaned = r.get("cleaned_data", {})
            ts_str = str(r.get("submission_timestamp", ""))
            row_vals = [r.get("response_number", 1), ts_str]
            for q in questions:
                val = cleaned.get(q["question_key"])
                if isinstance(val, list):
                    row_vals.append(sanitize_formula_cell(", ".join(str(x) for x in val)))
                elif val is not None:
                    row_vals.append(sanitize_formula_cell(val))
                else:
                    row_vals.append("")
            ws_clean.append(row_vals)

    # ----------------------------------------------------
    # Sheet 4: Question Statistics
    # ----------------------------------------------------
    ws_stats = wb.create_sheet(title="Statistics")
    ws_stats.append(["Question Key", "Question Text", "Type", "Metric", "Value"])
    for col_num in range(1, 6):
        cell = ws_stats.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font

    numerical = stats.get("numerical", {})
    for k, num in numerical.items():
        ws_stats.append([k, num.get("question_text"), "Numeric", "Count", num.get("count")])
        ws_stats.append([k, num.get("question_text"), "Numeric", "Mean", num.get("mean")])
        ws_stats.append([k, num.get("question_text"), "Numeric", "Median", num.get("median")])
        ws_stats.append([k, num.get("question_text"), "Numeric", "Std Dev", num.get("std_dev")])
        ws_stats.append([k, num.get("question_text"), "Numeric", "Min", num.get("min")])
        ws_stats.append([k, num.get("question_text"), "Numeric", "Max", num.get("max")])

    categorical = stats.get("categorical", {})
    for k, cat in categorical.items():
        for d in cat.get("distribution", []):
            ws_stats.append([k, cat.get("question_text"), "Categorical", str(d.get("label")), f"{d.get('count')} ({d.get('percentage')}%)"])

    # ----------------------------------------------------
    # Sheet 5: AI Insights
    # ----------------------------------------------------
    ws_insights = wb.create_sheet(title="AI Insights")
    ws_insights.append(["Category", "Insight / Finding"])
    ws_insights["A1"].fill = header_fill
    ws_insights["A1"].font = header_font
    ws_insights["B1"].fill = header_fill
    ws_insights["B1"].font = header_font

    for f in ai_insights.get("facts", []):
        ws_insights.append(["Calculated Fact", f])
    for item in ai_insights.get("interpretations", []):
        ws_insights.append(["Interpretation", item])
    for r in ai_insights.get("recommendations", []):
        ws_insights.append(["Recommendation", r])

    ws_insights.column_dimensions['A'].width = 20
    ws_insights.column_dimensions['B'].width = 80

    wb.save(file_path)
    return file_path
