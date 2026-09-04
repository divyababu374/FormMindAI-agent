import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional

GOOGLE_FORM_PATTERNS = [
    (r"https?://docs\.google\.com/forms/d/e/([a-zA-Z0-9_\-]+)", True, False),
    (r"https?://docs\.google\.com/forms/u/\d+/d/e/([a-zA-Z0-9_\-]+)", True, False),
    (r"https?://forms\.gle/([a-zA-Z0-9_\-]+)", True, True),
    (r"https?://docs\.google\.com/forms/u/\d+/d/([a-zA-Z0-9_\-]+)", False, False),
    (r"https?://docs\.google\.com/forms/d/([a-zA-Z0-9_\-]+)", False, False),
]

GOOGLE_SHEET_PATTERNS = [
    (r"https?://docs\.google\.com/spreadsheets/d/e/([a-zA-Z0-9_\-]+)", True),
    (r"https?://docs\.google\.com/spreadsheets/u/\d+/d/([a-zA-Z0-9_\-]+)", False),
    (r"https?://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_\-]+)", False),
]

MICROSOFT_FORM_PATTERNS = [
    # Response Page with ?id=
    r"https?://forms\.(?:office|microsoft)\.com/Pages/ResponsePage\.aspx\?.*?id=([a-zA-Z0-9_\-]+)",
    # Design Page with FormId=
    r"https?://forms\.(?:office|microsoft)\.com/Pages/DesignPage(?:V2)?\.aspx.*?FormId=([a-zA-Z0-9_\-]+)",
    # Short links: forms.office.com/r/... or forms.microsoft.com/r/...
    r"https?://forms\.(?:office|microsoft)\.com/r/([a-zA-Z0-9_\-]+)",
    # Embed links: forms.office.com/e/...
    r"https?://forms\.(?:office|microsoft)\.com/e/([a-zA-Z0-9_\-]+)",
]

def parse_and_validate_url(url: str) -> Dict[str, Any]:
    """
    Validates and extracts metadata from Google Forms, Google Sheets, or Microsoft Forms URLs.
    Returns dictionary with:
      - is_valid (bool)
      - source_type ('google_form', 'google_sheet', 'microsoft_form', or None)
      - resource_id (str)
      - normalized_url (str)
      - error_message (str or None)
    """
    if not url or not isinstance(url, str):
        return {
            "is_valid": False,
            "source_type": None,
            "resource_id": None,
            "normalized_url": None,
            "error_message": "Please enter a valid Google Forms, Microsoft Forms, or Google Sheets URL."
        }
    
    url = url.strip()
    
    # Check Google Form patterns
    for pattern, is_e_format, is_forms_gle in GOOGLE_FORM_PATTERNS:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            resource_id = match.group(1)
            # Skip false positives like 'e' matched inadvertently
            if resource_id == "e":
                continue

            if is_forms_gle:
                normalized = f"https://forms.gle/{resource_id}"
            elif is_e_format:
                normalized = f"https://docs.google.com/forms/d/e/{resource_id}/viewform"
            else:
                normalized = f"https://docs.google.com/forms/d/{resource_id}/viewform"

            return {
                "is_valid": True,
                "source_type": "google_form",
                "resource_id": resource_id,
                "normalized_url": normalized,
                "is_published_form": is_e_format or is_forms_gle,
                "is_short_url": is_forms_gle,
                "is_edit_responses": "#responses" in url or "/edit" in url,
                "error_message": None
            }
            
    # Check Google Sheet patterns
    for pattern, is_published_web in GOOGLE_SHEET_PATTERNS:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            resource_id = match.group(1)
            if resource_id == "e":
                continue

            if is_published_web:
                normalized = f"https://docs.google.com/spreadsheets/d/e/{resource_id}/pubhtml"
                export_csv = f"https://docs.google.com/spreadsheets/d/e/{resource_id}/pub?output=csv"
            else:
                normalized = f"https://docs.google.com/spreadsheets/d/{resource_id}/edit"
                export_csv = f"https://docs.google.com/spreadsheets/d/{resource_id}/export?format=csv"

            return {
                "is_valid": True,
                "source_type": "google_sheet",
                "resource_id": resource_id,
                "is_published_web": is_published_web,
                "normalized_url": normalized,
                "export_csv_url": export_csv,
                "error_message": None
            }

    # Check Microsoft Form patterns
    for pattern in MICROSOFT_FORM_PATTERNS:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            resource_id = match.group(1)
            is_short = "/r/" in url.lower() or "/e/" in url.lower()
            if is_short:
                normalized = f"https://forms.office.com/r/{resource_id}"
            else:
                normalized = f"https://forms.office.com/Pages/ResponsePage.aspx?id={resource_id}"

            return {
                "is_valid": True,
                "source_type": "microsoft_form",
                "resource_id": resource_id,
                "normalized_url": normalized,
                "is_short_url": is_short,
                "is_design_url": "design" in url.lower(),
                "error_message": None
            }

    # Fallback for any other forms.office.com or forms.microsoft.com URL
    parsed_u = urlparse(url)
    netloc = parsed_u.netloc.lower()
    if "forms.office.com" in netloc or "forms.microsoft.com" in netloc:
        q_params = parse_qs(parsed_u.query)
        res_id = None
        if "id" in q_params and q_params["id"]:
            res_id = q_params["id"][0]
        elif "FormId" in q_params and q_params["FormId"]:
            res_id = q_params["FormId"][0]
        else:
            # Check path segments
            path_parts = [p for p in parsed_u.path.split("/") if p]
            if len(path_parts) >= 2 and path_parts[0] in ("r", "e"):
                res_id = path_parts[1]
            elif path_parts:
                res_id = path_parts[-1]

        if res_id:
            return {
                "is_valid": True,
                "source_type": "microsoft_form",
                "resource_id": res_id,
                "normalized_url": f"https://forms.office.com/Pages/ResponsePage.aspx?id={res_id}",
                "is_short_url": "/r/" in url or "/e/" in url,
                "is_design_url": "design" in url.lower(),
                "error_message": None
            }

    return {
        "is_valid": False,
        "source_type": None,
        "resource_id": None,
        "normalized_url": url,
        "error_message": "Please enter a valid Google Forms URL (e.g. https://docs.google.com/forms/d/...) or Microsoft Forms URL (e.g. https://forms.office.com/r/...)."
    }
