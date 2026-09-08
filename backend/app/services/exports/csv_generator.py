import os
import csv
import datetime
from typing import Dict, Any, List
from app.config import settings

def sanitize_formula_cell(val: Any) -> str:
    """
    Prevents CSV / Spreadsheet Formula Injection (CWE-1236).
    If a cell string begins with =, +, -, @, \t, or \r, prepend a single quote (')
    so spreadsheet software renders it as text without executing formulas.
    """
    if val is None:
        return ""
    if isinstance(val, (int, float, bool)):
        return str(val)
    s = str(val)
    if s and s[0] in ('=', '+', '-', '@', '\t', '\r'):
        return "'" + s
    return s

def generate_csv_export(
    form_id: str,
    questions: List[Dict[str, Any]],
    responses: List[Dict[str, Any]]
) -> str:
    """
    Generates a clean, formula-injection-safe CSV file of the response dataset.
    """
    filename = f"FormMind_Dataset_{form_id[:8]}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    file_path = os.path.join(settings.EXPORTS_DIR, filename)

    headers = ["Response_ID", "Timestamp"]
    for q in questions:
        headers.append(sanitize_formula_cell(q["question_text"]))

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for r in responses:
            cleaned = r.get("cleaned_data", {})
            ts_str = str(r.get("submission_timestamp", ""))
            row = [r.get("response_number", 1), ts_str]
            for q in questions:
                val = cleaned.get(q["question_key"])
                if isinstance(val, list):
                    joined = ", ".join(str(x) for x in val)
                    row.append(sanitize_formula_cell(joined))
                elif val is not None:
                    row.append(sanitize_formula_cell(val))
                else:
                    row.append("")
            writer.writerow(row)

    return file_path
