import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_guest_unauthenticated_isolation():
    """Verify that unauthenticated / guest users have no access to data or forms."""
    # 1. Google status should be disconnected
    status_resp = client.get("/api/auth/google/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["is_connected"] is False
    assert status_data["email"] is None

    # 2. Forms list must be completely empty
    forms_resp = client.get("/api/forms")
    assert forms_resp.status_code == 200
    assert forms_resp.json() == []

    # 3. Unauthenticated analyze must be rejected with 401
    analyze_resp = client.post("/api/forms/analyze", json={"demo_type": "workshop_feedback"})
    assert analyze_resp.status_code == 401
    assert "connect" in analyze_resp.json()["detail"].lower()


def test_multi_user_data_isolation():
    """Verify strict data isolation between two distinct user accounts."""
    email_a = "test_user_alpha@formmind.ai"
    email_b = "test_user_beta@formmind.ai"

    # 1. Connect User Alpha
    auth_a = client.post("/api/auth/google/connect-email", json={"email": email_a, "name": "User Alpha"})
    assert auth_a.status_code == 200
    token_a = auth_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Verify Alpha Google Status
    status_a = client.get("/api/auth/google/status", headers=headers_a)
    assert status_a.status_code == 200
    assert status_a.json()["is_connected"] is True
    assert status_a.json()["email"] == email_a

    # Newly connected user must see empty forms list
    forms_a_init = client.get("/api/forms", headers=headers_a)
    assert forms_a_init.status_code == 200
    # Clean up any leftover forms from previous test runs if any
    for form in forms_a_init.json():
        client.delete(f"/api/forms/{form['id']}", headers=headers_a)

    forms_a_empty = client.get("/api/forms", headers=headers_a)
    assert forms_a_empty.json() == []

    # Alpha creates Form A
    create_a = client.post("/api/forms/analyze", json={"demo_type": "workshop_feedback"}, headers=headers_a)
    assert create_a.status_code == 200
    form_a = create_a.json()
    form_a_id = form_a["id"]

    # Alpha can access Form A
    assert client.get(f"/api/forms/{form_a_id}", headers=headers_a).status_code == 200
    assert client.get(f"/api/forms/{form_a_id}/analysis", headers=headers_a).status_code == 200

    # 2. Connect User Beta
    auth_b = client.post("/api/auth/google/connect-email", json={"email": email_b, "name": "User Beta"})
    assert auth_b.status_code == 200
    token_b = auth_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Verify Beta Google Status
    status_b = client.get("/api/auth/google/status", headers=headers_b)
    assert status_b.status_code == 200
    assert status_b.json()["is_connected"] is True
    assert status_b.json()["email"] == email_b

    # Clean up any leftover forms for Beta if any
    forms_b_init = client.get("/api/forms", headers=headers_b)
    for form in forms_b_init.json():
        client.delete(f"/api/forms/{form['id']}", headers=headers_b)

    # CRITICAL: User Beta MUST NOT see User Alpha's form in the forms list
    forms_b = client.get("/api/forms", headers=headers_b)
    assert forms_b.status_code == 200
    beta_form_ids = [f["id"] for f in forms_b.json()]
    assert form_a_id not in beta_form_ids
    assert len(beta_form_ids) == 0

    # CRITICAL: User Beta MUST NOT be able to view, analyze, chat with, or export Form A
    assert client.get(f"/api/forms/{form_a_id}", headers=headers_b).status_code == 404
    assert client.get(f"/api/forms/{form_a_id}/analysis", headers=headers_b).status_code == 404
    assert client.get(f"/api/forms/{form_a_id}/chat/history", headers=headers_b).status_code == 404
    assert client.post(f"/api/forms/{form_a_id}/chat", json={"content": "Summarize this"}, headers=headers_b).status_code == 404
    assert client.get(f"/api/forms/{form_a_id}/export/summary", headers=headers_b).status_code == 404

    # User Beta creates their own Form B
    create_b = client.post("/api/forms/analyze", json={"demo_type": "customer_nps"}, headers=headers_b)
    assert create_b.status_code == 200
    form_b_id = create_b.json()["id"]

    # Beta sees only Form B
    forms_b_after = client.get("/api/forms", headers=headers_b).json()
    b_ids = [f["id"] for f in forms_b_after]
    assert form_b_id in b_ids
    assert form_a_id not in b_ids

    # Alpha sees only Form A
    forms_a_after = client.get("/api/forms", headers=headers_a).json()
    a_ids = [f["id"] for f in forms_a_after]
    assert form_a_id in a_ids
    assert form_b_id not in a_ids

    # Alpha cannot access Form B
    assert client.get(f"/api/forms/{form_b_id}", headers=headers_a).status_code == 404

    # Clean up test forms
    client.delete(f"/api/forms/{form_a_id}", headers=headers_a)
    client.delete(f"/api/forms/{form_b_id}", headers=headers_b)
