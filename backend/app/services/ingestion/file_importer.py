import io
import pandas as pd
from typing import Dict, Any
from app.services.ingestion.google_connector import GoogleConnector

def import_file_to_dataset(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Imports CSV or Excel (XLSX/XLS) binary content and converts it into a standardized form dataset.
    """
    clean_title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
    
    if filename.lower().endswith((".xlsx", ".xls")):
        # Read Excel using pandas
        excel_file = io.BytesIO(file_bytes)
        df = pd.read_excel(excel_file)
        # Convert df to csv text and reuse robust parser
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return GoogleConnector.parse_csv_content(csv_buffer.getvalue(), source_title=clean_title)
    else:
        # Default CSV
        csv_text = file_bytes.decode("utf-8", errors="replace")
        return GoogleConnector.parse_csv_content(csv_text, source_title=clean_title)
