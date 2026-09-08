import re
import socket
import ipaddress
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional, Tuple

ALLOWED_HOSTS = {
    "docs.google.com",
    "forms.gle",
    "forms.office.com",
    "forms.microsoft.com",
}

def is_ip_private_or_reserved(ip_str: str) -> bool:
    """
    Checks if an IP address is private, loopback, link-local, multicast, or reserved.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private or
            ip.is_loopback or
            ip.is_link_local or
            ip.is_multicast or
            ip.is_reserved or
            ip.is_unspecified or
            str(ip) in ("0.0.0.0", "169.254.169.254", "::1")
        )
    except ValueError:
        return True

def validate_ssrf_safe_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that a URL is safe from SSRF attacks:
    1. Scheme must strictly be https://
    2. Hostname must belong to allowed Google/Microsoft domains
    3. Hostname cannot resolve to a private or internal IP address
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme.lower() != "https":
            return False, "Only secure HTTPS URLs are permitted."

        host = parsed.hostname
        if not host:
            return False, "Invalid URL host."

        host_lower = host.lower()
        # Verify host against allowed domain whitelist
        is_allowed = any(host_lower == allowed or host_lower.endswith(f".{allowed}") for allowed in ALLOWED_HOSTS)
        if not is_allowed:
            return False, "Please enter a valid Google Forms URL (e.g. https://docs.google.com/forms/d/...) or Microsoft Forms URL (e.g. https://forms.office.com/r/...)."

        # Verify DNS resolution does not point to internal/private IP
        try:
            addr_info = socket.getaddrinfo(host, 443, socket.AF_UNSPEC, socket.SOCK_STREAM)
            for item in addr_info:
                ip_addr = item[4][0]
                if is_ip_private_or_reserved(ip_addr):
                    return False, "Target address resolves to a restricted private or internal IP."
        except socket.gaierror:
            # Domain could not be resolved
            return False, "Could not resolve hostname for the provided URL."

        return True, None
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"

GOOGLE_FORM_PATTERNS = [
    (r"^https://docs\.google\.com/forms/d/e/([a-zA-Z0-9_\-]+)", True, False),
    (r"^https://docs\.google\.com/forms/u/\d+/d/e/([a-zA-Z0-9_\-]+)", True, False),
    (r"^https://forms\.gle/([a-zA-Z0-9_\-]+)", True, True),
    (r"^https://docs\.google\.com/forms/u/\d+/d/([a-zA-Z0-9_\-]+)", False, False),
    (r"^https://docs\.google\.com/forms/d/([a-zA-Z0-9_\-]+)", False, False),
]

GOOGLE_SHEET_PATTERNS = [
    (r"^https://docs\.google\.com/spreadsheets/d/e/([a-zA-Z0-9_\-]+)", True),
    (r"^https://docs\.google\.com/spreadsheets/u/\d+/d/([a-zA-Z0-9_\-]+)", False),
    (r"^https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9_\-]+)", False),
]

MICROSOFT_FORM_PATTERNS = [
    # Response Page with ?id=
    r"^https://forms\.(?:office|microsoft)\.com/Pages/ResponsePage\.aspx\?.*?id=([a-zA-Z0-9_\-]+)",
    # Design Page with FormId=
    r"^https://forms\.(?:office|microsoft)\.com/Pages/DesignPage(?:V2)?\.aspx.*?FormId=([a-zA-Z0-9_\-]+)",
    # Short links: forms.office.com/r/... or forms.microsoft.com/r/...
    r"^https://forms\.(?:office|microsoft)\.com/r/([a-zA-Z0-9_\-]+)",
    # Embed links: forms.office.com/e/...
    r"^https://forms\.(?:office|microsoft)\.com/e/([a-zA-Z0-9_\-]+)",
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
            "error_message": "Please enter a valid Google Forms or Google Sheets URL."
        }
    
    url = url.strip()

    # Prepend https:// if user pasted a raw domain like docs.google.com/...
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # SSRF & Protocol Validation
    is_safe, ssrf_err = validate_ssrf_safe_url(url)
    if not is_safe:
        return {
            "is_valid": False,
            "source_type": None,
            "resource_id": None,
            "normalized_url": url,
            "error_message": ssrf_err or "Invalid or untrusted URL."
        }
    
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
