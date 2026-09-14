import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "FormMind AI" in data["service"]

def test_auth_and_google_config():
    config_resp = client.get("/api/auth/google/config")
    assert config_resp.status_code == 200
    assert "is_configured" in config_resp.json()

def test_demo_form_analyze_flow():
    # 0. Authenticate test user
    auth_resp = client.post("/api/auth/google/connect-email", json={"email": "demo-test@formmind.ai", "name": "Demo Tester"})
    assert auth_resp.status_code == 200
    token = auth_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Ingest Demo Form
    analyze_resp = client.post("/api/forms/analyze", json={"demo_type": "workshop_feedback"}, headers=headers)
    assert analyze_resp.status_code == 200
    form_data = analyze_resp.json()
    form_id = form_data["id"]
    assert form_data["total_responses_count"] == 248
    assert form_data["questions_count"] > 5

    # 2. Get Forms List & Form Detail
    list_resp = client.get("/api/forms", headers=headers)
    assert list_resp.status_code == 200
    assert all(f["id"] != form_id for f in list_resp.json())

    detail_resp = client.get(f"/api/forms/{form_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert len(detail_resp.json()["questions"]) > 5

    questions_resp = client.get(f"/api/forms/{form_id}/questions", headers=headers)
    assert questions_resp.status_code == 200
    assert len(questions_resp.json()) > 5

    # 3. Get Analysis
    analysis_resp = client.get(f"/api/forms/{form_id}/analysis", headers=headers)
    assert analysis_resp.status_code == 200
    analysis = analysis_resp.json()
    assert "numerical_analysis" in analysis
    assert "categorical_analysis" in analysis
    assert "ai_insights" in analysis

    # 4. Get Responses (Paginated)
    responses_resp = client.get(f"/api/forms/{form_id}/responses?page=1&page_size=10", headers=headers)
    assert responses_resp.status_code == 200
    resp_page = responses_resp.json()
    assert resp_page["total"] == 248
    assert len(resp_page["items"]) == 10

    # 5. Send Chat Message & Check History
    chat_resp = client.post(f"/api/forms/{form_id}/chat", json={"content": "What is the average rating?"}, headers=headers)
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert chat_data["role"] == "assistant"
    assert "content" in chat_data

    history_resp = client.get(f"/api/forms/{form_id}/chat/history", headers=headers)
    assert history_resp.status_code == 200
    assert len(history_resp.json()["messages"]) >= 2

    # 6. Generate Custom Reports for all 4 distinct presets
    r_full = client.post(f"/api/forms/{form_id}/report", json={"report_type": "full"}, headers=headers)
    assert r_full.status_code == 200
    assert "Full 10-Section Analysis" in r_full.json()["content_markdown"]
    assert "10. Conclusion & Strategic Roadmap" in r_full.json()["content_markdown"]

    r_exec = client.post(f"/api/forms/{form_id}/report", json={"report_type": "executive_summary"}, headers=headers)
    assert r_exec.status_code == 200
    assert "Executive Brief (1-Page)" in r_exec.json()["content_markdown"]
    assert "Leadership KPI Scorecard" in r_exec.json()["content_markdown"]

    r_neg = client.post(f"/api/forms/{form_id}/report", json={"report_type": "negative_feedback"}, headers=headers)
    assert r_neg.status_code == 200
    assert "Critiques & Friction Points" in r_neg.json()["content_markdown"]
    assert "Problem Statement & Friction Overview" in r_neg.json()["content_markdown"]

    r_lead = client.post(f"/api/forms/{form_id}/report", json={"report_type": "leadership"}, headers=headers)
    assert r_lead.status_code == 200
    assert "Executive Presentation" in r_lead.json()["content_markdown"]
    assert "Boardroom Performance Metrics Matrix" in r_lead.json()["content_markdown"]

    # 7. Export Files
    pdf_resp = client.get(f"/api/forms/{form_id}/export/pdf", headers=headers)
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"

    csv_resp = client.get(f"/api/forms/{form_id}/export/csv", headers=headers)
    assert csv_resp.status_code == 200

    xlsx_resp = client.get(f"/api/forms/{form_id}/export/xlsx", headers=headers)
    assert xlsx_resp.status_code == 200

    docx_resp = client.get(f"/api/forms/{form_id}/export/docx", headers=headers)
    assert docx_resp.status_code == 200

    img_resp = client.post(f"/api/forms/{form_id}/image?format=png", headers=headers)
    assert img_resp.status_code == 200
    assert img_resp.headers["content-type"] == "image/png"

    img_get_resp = client.get(f"/api/forms/{form_id}/image?format=png", headers=headers)
    assert img_get_resp.status_code == 200
    assert img_get_resp.headers["content-type"] == "image/png"

    # 8. Delete Form
    delete_resp = client.delete(f"/api/forms/{form_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "success"
