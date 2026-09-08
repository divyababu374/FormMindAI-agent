import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)

def test_health_probes():
    # 1. Base /health
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "FormMind AI"
    assert "version" in data

    # 2. Liveness probe
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    # 3. Readiness probe
    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"
    assert ready_res.json()["database"] == "connected"

def test_security_headers_present():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in res.headers.get("Permissions-Policy", "")

def test_request_id_and_timing_headers():
    # Auto-generated Request ID
    res = client.get("/health")
    assert "X-Request-ID" in res.headers
    assert "X-Response-Time" in res.headers
    assert res.headers["X-Response-Time"].endswith("ms")

    # Client-supplied Request ID preservation
    custom_id = "test-req-custom-uuid-12345"
    res_custom = client.get("/health", headers={"X-Request-ID": custom_id})
    assert res_custom.headers.get("X-Request-ID") == custom_id

def test_rfc7807_error_formatting():
    # 404 Form Not Found
    res = client.get("/api/forms/non-existent-form-id-999")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert "detail" in data
    assert data["status_code"] == 404
    assert "request_id" in data
