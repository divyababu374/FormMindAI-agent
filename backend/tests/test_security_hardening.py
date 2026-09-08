import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.ingestion.url_parser import parse_and_validate_url, validate_ssrf_safe_url, is_ip_private_or_reserved
from app.services.ingestion.file_importer import import_file_to_dataset, sanitize_filename
from app.services.exports.csv_generator import sanitize_formula_cell, generate_csv_export
from app.services.exports.xlsx_generator import sanitize_formula_cell as sanitize_xlsx_cell
from app.utils.security import create_access_token, decode_token_payload

client = TestClient(app)

# ==============================================================================
# 1. SSRF & URL Whitelist Security Tests
# ==============================================================================

def test_ssrf_blocks_localhost_and_private_ips():
    # Loopback IP
    assert is_ip_private_or_reserved("127.0.0.1") is True
    # Private RFC1918 IPs
    assert is_ip_private_or_reserved("10.0.0.1") is True
    assert is_ip_private_or_reserved("192.168.1.1") is True
    assert is_ip_private_or_reserved("172.16.0.1") is True
    # Link-local / Cloud Metadata IP
    assert is_ip_private_or_reserved("169.254.169.254") is True
    assert is_ip_private_or_reserved("0.0.0.0") is True

def test_ssrf_blocks_invalid_schemes_and_untrusted_domains():
    # Insecure HTTP
    safe, err = validate_ssrf_safe_url("http://docs.google.com/forms/d/e/123/viewform")
    assert safe is False
    assert "Only secure HTTPS URLs are permitted" in err

    # Untrusted domain
    safe, err = validate_ssrf_safe_url("https://malicious-site.com/fakeform")
    assert safe is False
    assert "Please enter a valid Google Forms URL" in err

    # File and Javascript schemes
    res = parse_and_validate_url("file:///etc/passwd")
    assert res["is_valid"] is False

    res = parse_and_validate_url("javascript:alert(1)")
    assert res["is_valid"] is False

def test_ssrf_allows_legitimate_google_and_microsoft_urls():
    res = parse_and_validate_url("https://docs.google.com/forms/d/e/1FAIpQLScABCDEF123456/viewform")
    assert res["is_valid"] is True
    assert res["source_type"] == "google_form"

    res = parse_and_validate_url("https://forms.office.com/r/abcdef123")
    assert res["is_valid"] is True
    assert res["source_type"] == "microsoft_form"


# ==============================================================================
# 2. File Upload & Ingestion Security Tests
# ==============================================================================

def test_filename_sanitization_removes_path_traversal():
    assert sanitize_filename("../../etc/passwd.csv") == "passwd.csv"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.exe.csv") == "calc.exe.csv"
    assert sanitize_filename("safe_feedback.xlsx") == "safe_feedback.xlsx"
    assert sanitize_filename("") == "dataset.csv"

def test_file_importer_rejects_disallowed_extensions():
    # Macro-enabled Excel (.xlsm)
    with pytest.raises(ValueError) as exc:
        import_file_to_dataset(b"fake macro bytes", "payroll.xlsm")
    assert "macro-enabled" in str(exc.value)

    # Executable file (.exe)
    with pytest.raises(ValueError) as exc:
        import_file_to_dataset(b"MZ\x90\x00", "installer.exe")
    assert "prohibited" in str(exc.value)

    # Shell script (.sh)
    with pytest.raises(ValueError) as exc:
        import_file_to_dataset(b"#!/bin/sh", "script.sh")
    assert "prohibited" in str(exc.value)

def test_file_importer_rejects_empty_payload():
    with pytest.raises(ValueError) as exc:
        import_file_to_dataset(b"", "empty.csv")
    assert "empty" in str(exc.value)

def test_file_importer_parses_valid_csv_safely():
    csv_bytes = b"Timestamp,Rating,Feedback\n2026-01-01,5,Great session\n2026-01-02,4,Good pacing\n"
    dataset = import_file_to_dataset(csv_bytes, "valid_survey.csv")
    assert dataset is not None
    assert len(dataset["responses"]) == 2
    assert len(dataset["questions"]) >= 2


# ==============================================================================
# 3. CSV & Spreadsheet Formula Injection (CWE-1236) Defense Tests
# ==============================================================================

def test_csv_formula_injection_escaping():
    # Formula payloads starting with =, +, -, @, TAB, CR
    assert sanitize_formula_cell("=CMD|' /C calc'!A0") == "'=CMD|' /C calc'!A0"
    assert sanitize_formula_cell("+123456") == "'+123456"
    assert sanitize_formula_cell("-SUM(A1:A10)") == "'-SUM(A1:A10)"
    assert sanitize_formula_cell("@SUM(1+1)") == "'@SUM(1+1)"
    assert sanitize_formula_cell("\tMALICIOUS") == "'\tMALICIOUS"

    # Clean text and numbers should remain intact
    assert sanitize_formula_cell("Great workshop!") == "Great workshop!"
    assert sanitize_formula_cell(4.5) == "4.5"
    assert sanitize_formula_cell(100) == "100"
    assert sanitize_formula_cell(None) == ""

def test_xlsx_formula_injection_escaping():
    assert sanitize_xlsx_cell("=1+1") == "'=1+1"
    assert sanitize_xlsx_cell(5) == 5
    assert sanitize_xlsx_cell("Normal Feedback") == "Normal Feedback"


# ==============================================================================
# 4. Authentication & Token Security Tests
# ==============================================================================

def test_token_creation_and_payload_decoding():
    token = create_access_token(subject="user_sec_123")
    payload = decode_token_payload(token)
    assert payload is not None
    assert payload.get("sub") == "user_sec_123"

def test_invalid_and_malformed_tokens_rejected():
    assert decode_token_payload("") is None
    assert decode_token_payload("invalid.token.string") is None
    assert decode_token_payload("Bearer completely_bogus_token") is None


# ==============================================================================
# 5. Security Response Headers & Caching Tests
# ==============================================================================

def test_security_headers_present_on_api_responses():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert response.headers.get("Permissions-Policy") == "camera=(), microphone=(), geolocation=()"
    assert "frame-ancestors 'self'" in response.headers.get("Content-Security-Policy", "")

def test_authenticated_routes_have_no_cache_headers():
    response = client.get("/api/forms")
    assert response.headers.get("Cache-Control") is not None
    assert "no-store" in response.headers.get("Cache-Control")
    assert "no-cache" in response.headers.get("Cache-Control")
