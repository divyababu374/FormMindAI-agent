import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.ingestion.google_connector import GoogleConnector

client = TestClient(app)

def test_extract_viewanalytics_responses():
    mock_analytics_data = [
        None,
        [
            None,
            [
                # Question 1: Rating
                [None, "Overall Experience", None, 5, [None, [["5", 10], ["4", 15], ["3", 5]]]],
                # Question 2: Categorical
                [None, "Department", None, 2, [None, [["Engineering", 18], ["Marketing", 12]]]]
            ]
        ]
    ]
    questions = [
        {"question_key": "Q1", "question_text": "Overall Experience", "question_type": "rating", "inferred_data_type": "numeric"},
        {"question_key": "Q2", "question_text": "Department", "question_type": "multiple_choice", "inferred_data_type": "categorical"}
    ]

    responses = GoogleConnector._extract_viewanalytics_responses(mock_analytics_data, questions)
    assert len(responses) == 30  # Max respondents between 30 and 30
    assert responses[0]["cleaned_data"]["Q1"] is not None
    assert responses[0]["cleaned_data"]["Q2"] is not None

def test_attach_sheet_flow():
    # 1. Create a demo form with 0 responses (or a form)
    create_resp = client.post("/api/forms/analyze", json={"demo_type": "customer_nps"})
    assert create_resp.status_code == 200
    form_id = create_resp.json()["id"]

    # 2. Mock GoogleConnector.fetch_from_sheet_url
    mock_sheet_data = {
        "title": "Linked Responses Sheet",
        "questions": [
            {"question_key": "Q1", "question_text": "How likely are you to recommend us to a friend or colleague? (0-10)", "question_type": "rating"}
        ],
        "responses": [
            {
                "response_number": 1,
                "raw_data": {"How likely are you to recommend us to a friend or colleague? (0-10)": 10},
                "cleaned_data": {"Q1": 10}
            },
            {
                "response_number": 2,
                "raw_data": {"How likely are you to recommend us to a friend or colleague? (0-10)": 9},
                "cleaned_data": {"Q1": 9}
            }
        ]
    }

    with patch.object(GoogleConnector, "fetch_from_sheet_url", return_value=mock_sheet_data):
        attach_resp = client.post(
            f"/api/forms/{form_id}/attach-sheet",
            json={"sheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"}
        )
        assert attach_resp.status_code == 200
        assert attach_resp.json()["response_access_status"] == "ready"

    # Cleanup
    client.delete(f"/api/forms/{form_id}")

def test_upload_responses_flow():
    create_resp = client.post("/api/forms/analyze", json={"demo_type": "workshop_feedback"})
    assert create_resp.status_code == 200
    form_id = create_resp.json()["id"]

    csv_content = b"Timestamp,Overall Rating (1-5),Session Topic Relevance\n2026-03-01 10:00:00,5,5\n2026-03-01 10:05:00,4,4\n"
    
    upload_resp = client.post(
        f"/api/forms/{form_id}/upload-responses",
        files={"file": ("responses.csv", csv_content, "text/csv")}
    )
    assert upload_resp.status_code == 200
    assert upload_resp.json()["response_access_status"] == "ready"

    client.delete(f"/api/forms/{form_id}")

def test_drive_form_resolution_and_authorized_fetch():
    mock_files_resp = MagicMock()
    mock_files_resp.status_code = 200
    mock_files_resp.json.return_value = {
        "files": [
            {"id": "drive_form_123", "name": "Employee Survey 2026", "modifiedTime": "2026-03-01T10:00:00Z"}
        ]
    }

    with patch("requests.get", return_value=mock_files_resp):
        resolved_id = GoogleConnector.resolve_drive_form_id_by_title("Employee Survey 2026", "mock_token")
        assert resolved_id == "drive_form_123"

        forms_list = GoogleConnector.list_user_drive_forms("mock_token")
        assert len(forms_list) == 1
        assert forms_list[0]["id"] == "drive_form_123"
        assert forms_list[0]["edit_url"] == "https://docs.google.com/forms/d/drive_form_123/edit"

def test_google_auth_status_endpoint():
    resp = client.get("/api/auth/google/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "is_connected" in data
    assert "is_oauth_configured" in data

