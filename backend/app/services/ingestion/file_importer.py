import io
import os
import re
import pandas as pd
from typing import Dict, Any
from app.services.ingestion.google_connector import GoogleConnector

ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
DISALLOWED_EXTENSIONS = {".xlsm", ".xltm", ".exe", ".js", ".py", ".sh", ".bat", ".vbs", ".cmd", ".dll"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MAX_ROWS = 50000
MAX_COLS = 200

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user-supplied filenames to prevent path traversal and shell exploits.
    """
    if not filename or not isinstance(filename, str):
        return "dataset.csv"
    # Remove null bytes, path traversal sequences, directory delimiters
    clean = filename.replace("\x00", "").replace("../", "").replace("..\\", "")
    clean = os.path.basename(clean)
    # Strip dangerous characters
    clean = re.sub(r'[^a-zA-Z0-9_\-\. ]', '_', clean)
    return clean.strip() or "dataset.csv"

def import_file_to_dataset(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Securely imports CSV or Excel (XLSX/XLS) binary content and converts it into a standardized form dataset.
    Validates file sizes, extensions, and content constraints.
    """
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB.")

    safe_filename = sanitize_filename(filename)
    _, ext = os.path.splitext(safe_filename.lower())

    if ext in DISALLOWED_EXTENSIONS:
        raise ValueError(f"File extension '{ext}' is prohibited for security reasons (macro-enabled spreadsheets and executables are not allowed).")

    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file format '{ext}'. Only .csv, .xlsx, and .xls files are supported.")

    clean_title = safe_filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    if ext in (".xlsx", ".xls"):
        try:
            excel_file = io.BytesIO(file_bytes)
            # Read first sheet with safety limits on rows and columns
            df = pd.read_excel(excel_file, nrows=MAX_ROWS)
            if df.shape[1] > MAX_COLS:
                df = df.iloc[:, :MAX_COLS]
            if df.empty:
                raise ValueError("The spreadsheet contains no data rows.")
            # Convert df to csv text and reuse robust parser
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return GoogleConnector.parse_csv_content(csv_buffer.getvalue(), source_title=clean_title)
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to process spreadsheet: {str(e)}")
    else:
        # Default CSV with encoding fallback
        try:
            csv_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                csv_text = file_bytes.decode("latin-1")
            except Exception:
                csv_text = file_bytes.decode("utf-8", errors="replace")

        if not csv_text.strip():
            raise ValueError("The CSV file is empty.")

        return GoogleConnector.parse_csv_content(csv_text, source_title=clean_title)
