import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.account import ConnectedAccount, ConnectedDriveForm
from app.models.form import Form
from app.models.question import FormQuestion
from app.models.response import FormResponse
from app.models.analysis import FormAnalysis

client = TestClient(app)

def test_connected_email_and_forms_saved_in_database():
    test_email = "analyst.pro@gmail.com"
    test_name = "Jane Analyst"

    # 1. Connect email via POST /api/auth/google/connect-email
    resp = client.post("/api/auth/google/connect-email", json={
        "email": test_email,
        "name": test_name
    })
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["is_connected"] is True
    assert data["email"] == test_email
    assert data["name"] == test_name
    auth_token = data["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. Verify connected email details are in the database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == test_email).first()
        assert user is not None, "User record must exist in database"
        assert user.is_google_connected is True
        assert user.full_name == test_name

        account = db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == user.id,
            ConnectedAccount.email == test_email,
            ConnectedAccount.provider == "google"
        ).first()
        assert account is not None, "ConnectedAccount must be saved in database"
        assert account.is_active is True
        assert account.name == test_name
        assert account.connected_at is not None

        # 3. Ingest a form for this user and verify full persistence
        form_resp = client.post(
            "/api/forms/analyze",
            json={"demo_type": "customer_nps", "title": "Customer Loyalty & NPS 2026"},
            headers=headers
        )
        assert form_resp.status_code == 200, form_resp.text
        form_data = form_resp.json()
        form_id = form_data["id"]

        # Check form record in database
        saved_form = db.query(Form).filter(Form.id == form_id).first()
        assert saved_form is not None, "Form must be saved in database"
        assert saved_form.user_id == user.id
        assert saved_form.connected_email == test_email
        assert saved_form.title == "Customer Loyalty & NPS 2026"
        assert saved_form.total_responses_count > 0

        # Check questions saved in database
        saved_questions = db.query(FormQuestion).filter(FormQuestion.form_id == form_id).all()
        assert len(saved_questions) > 0, "Form questions must be saved in database"

        # Check responses saved in database
        saved_responses = db.query(FormResponse).filter(FormResponse.form_id == form_id).all()
        assert len(saved_responses) == saved_form.total_responses_count, "All responses must be saved in database"

        # Check analysis saved in database
        saved_analysis = db.query(FormAnalysis).filter(FormAnalysis.form_id == form_id).first()
        assert saved_analysis is not None, "Form analysis must be saved in database"
        assert saved_analysis.ai_insights is not None

        # 4. Check /api/auth/google/status endpoint returns DB saved stats
        status_resp = client.get("/api/auth/google/status", headers=headers)
        assert status_resp.status_code == 200
        st = status_resp.json()
        assert st["is_connected"] is True
        assert st["email"] == test_email
        assert st["name"] == test_name
        assert st["connected_forms_count"] >= 1

        # 5. Check forms list endpoint returns the form
        forms_resp = client.get("/api/forms", headers=headers)
        assert forms_resp.status_code == 200
        forms_list = forms_resp.json()
        assert any(f["id"] == form_id for f in forms_list)

        # 6. Disconnect Google account and verify database update
        disc_resp = client.post("/api/auth/google/disconnect", headers=headers)
        assert disc_resp.status_code == 200

        # Verify in database
        db.refresh(user)
        assert user.is_google_connected is False
        db.refresh(account)
        assert account.is_active is False

    finally:
        db.close()


def test_stale_token_auto_heals_and_connects_email():
    from app.utils.security import create_access_token
    # Generate token for a user that does NOT exist in DB
    fake_token = create_access_token("non_existent_ghost_user_id_12345")
    headers = {"Authorization": f"Bearer {fake_token}"}

    # Should succeed without 401 "User not found or inactive"
    resp = client.post("/api/auth/google/connect-email", json={
        "email": "divyababu374@gmail.com",
        "name": "Divya Babu"
    }, headers=headers)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["is_connected"] is True
    assert data["email"] == "divyababu374@gmail.com"

