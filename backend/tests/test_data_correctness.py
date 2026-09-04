import pytest
import uuid
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.form import Form
from app.models.question import FormQuestion
from app.models.response import FormResponse, ResponseAnswer
from app.models.attachment import Attachment
from app.models.analysis import FormAnalysis
from app.api.forms import _process_and_save_dataset
from app.services.analytics.stats_engine import StatsEngine
from app.services.chat.grounded_chat import GroundedChatEngine
from app.services.exports.csv_generator import generate_csv_export

# In-memory test SQLite database
engine = create_engine("sqlite:///:memory:", echo=False)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Create test user
    test_user = User(
        id=str(uuid.uuid4()),
        email="tester@formmind.ai",
        full_name="Tester Quality",
        is_active=True
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    
    yield session, test_user
    
    session.close()
    Base.metadata.drop_all(bind=engine)


# ==============================================================================
# TEST 1 — Response Count Consistency
# ==============================================================================
def test_1_response_count_consistency(db_session):
    db, user = db_session
    
    # Create dataset with exactly 10 responses
    questions = [
        {"question_key": "Q1", "question_text": "Rating", "question_type": "rating", "inferred_data_type": "numeric", "options": ["1", "2", "3", "4", "5"], "scale_min": 1, "scale_max": 5}
    ]
    responses = [
        {
            "response_number": i,
            "submission_timestamp": datetime.datetime.utcnow(),
            "raw_data": {"Rating": str(i % 5 + 1)},
            "cleaned_data": {"Q1": float(i % 5 + 1)},
            "is_valid": True
        }
        for i in range(1, 11)
    ]
    dataset = {
        "title": "Customer Feedback Survey",
        "questions": questions,
        "responses": responses,
        "source_type": "google_form",
        "response_access_status": "ready"
    }

    # 1. Ingest into database
    form = _process_and_save_dataset(dataset, user, db)

    # 2. Verify Database count
    db_count = db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
    assert db_count == 10
    assert form.total_responses_count == 10

    # 3. Verify Analytics count
    stats = StatsEngine.calculate_all(questions, responses)
    assert stats["basic"]["total_responses"] == 10

    # 4. Verify AI Chat query
    chat_res = GroundedChatEngine.process_query(
        user_message="How many responded to the form?",
        form=form,
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )
    assert "10 people responded" in chat_res["content"] or "10 respondents" in chat_res["content"]

    # 5. Verify Export CSV row count
    csv_file = generate_csv_export(form.id, questions, responses)
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = [line for line in f.read().strip().split("\n") if line]
    # Header + 10 rows
    assert len(lines) == 11


# ==============================================================================
# TEST 2 — Zero Responses Handling
# ==============================================================================
def test_2_zero_responses(db_session):
    db, user = db_session

    questions = [
        {"question_key": "Q1", "question_text": "Satisfaction", "question_type": "rating", "inferred_data_type": "numeric", "options": ["1", "2", "3", "4", "5"], "scale_min": 1, "scale_max": 5}
    ]
    dataset = {
        "title": "Empty Form",
        "questions": questions,
        "responses": [],
        "source_type": "google_form",
        "response_access_status": "zero_responses"
    }

    # Ingest empty form
    form = _process_and_save_dataset(dataset, user, db)

    # 1. Verify response count is 0
    db_count = db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
    assert db_count == 0
    assert form.total_responses_count == 0

    # 2. Verify no fake responses created
    all_responses = db.query(FormResponse).filter(FormResponse.form_id == form.id).all()
    assert len(all_responses) == 0

    # 3. Verify no fake insights
    analysis = db.query(FormAnalysis).filter(FormAnalysis.form_id == form.id).first()
    assert "0 responses" in analysis.executive_summary
    assert form.analysis_status == "unavailable"

    # 4. Verify Chat replies "This form currently has 0 responses."
    chat_res = GroundedChatEngine.process_query(
        user_message="How many responded?",
        form=form,
        questions=questions,
        responses=[],
        analysis_data={},
        chat_history=[]
    )
    assert "0 responses" in chat_res["content"]


# ==============================================================================
# TEST 3 — Percentage Calculation
# ==============================================================================
def test_3_percentage_calculation():
    # 50 responses, 30 say Yes, 20 say No
    questions = [
        {"question_key": "Q1", "question_text": "Do you recommend this?", "question_type": "yes_no", "inferred_data_type": "categorical", "options": ["Yes", "No"]}
    ]
    responses = []
    for i in range(30):
        responses.append({"response_number": i + 1, "cleaned_data": {"Q1": "Yes"}, "is_valid": True})
    for i in range(20):
        responses.append({"response_number": 31 + i, "cleaned_data": {"Q1": "No"}, "is_valid": True})

    # 1. Analytics calculation
    stats = StatsEngine.calculate_all(questions, responses)
    dist = stats["categorical"]["Q1"]["distribution"]
    yes_item = next(d for d in dist if d["label"] == "Yes")
    no_item = next(d for d in dist if d["label"] == "No")
    
    assert yes_item["count"] == 30
    assert yes_item["percentage"] == 60.0
    assert no_item["count"] == 20
    assert no_item["percentage"] == 40.0

    # 2. Chat answers 60%
    class MockForm:
        title = "Survey"
        completion_rate = "100%"
        response_access_status = "ready"
    
    chat_res = GroundedChatEngine.process_query(
        user_message="How many selected Yes?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data=stats,
        chat_history=[]
    )
    assert "30 people" in chat_res["content"]
    assert "60.0%" in chat_res["content"] or "60%" in chat_res["content"]


# ==============================================================================
# TEST 4 — Average Calculation
# ==============================================================================
def test_4_average_calculation():
    # Ratings: 1, 2, 3, 4, 5 -> mean should be exactly 3.0
    questions = [
        {"question_key": "Q1", "question_text": "Overall Score", "question_type": "rating", "inferred_data_type": "numeric", "options": ["1", "2", "3", "4", "5"], "scale_min": 1, "scale_max": 5}
    ]
    responses = [
        {"response_number": i, "cleaned_data": {"Q1": float(i)}, "is_valid": True}
        for i in range(1, 6)
    ]

    stats = StatsEngine.calculate_all(questions, responses)
    assert stats["numerical"]["Q1"]["mean"] == 3.0

    class MockForm:
        title = "Ratings Survey"
        completion_rate = "100%"
        response_access_status = "ready"

    chat_res = GroundedChatEngine.process_query(
        user_message="What is the average rating?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data=stats,
        chat_history=[]
    )
    assert "3.0" in chat_res["content"]


# ==============================================================================
# TEST 5 — Form Isolation
# ==============================================================================
def test_5_form_isolation(db_session):
    db, user = db_session

    q = [{"question_key": "Q1", "question_text": "Score", "question_type": "rating", "inferred_data_type": "numeric"}]
    
    # Form A with 10 responses
    dataset_a = {
        "title": "Form A",
        "questions": q,
        "responses": [{"response_number": i + 1, "raw_data": {"Score": "5"}, "cleaned_data": {"Q1": 5.0}} for i in range(10)]
    }
    form_a = _process_and_save_dataset(dataset_a, user, db)

    # Form B with 20 responses
    dataset_b = {
        "title": "Form B",
        "questions": q,
        "responses": [{"response_number": i + 1, "raw_data": {"Score": "4"}, "cleaned_data": {"Q1": 4.0}} for i in range(20)]
    }
    form_b = _process_and_save_dataset(dataset_b, user, db)

    # Verify counts are isolated in DB
    count_a = db.query(FormResponse).filter(FormResponse.form_id == form_a.id).count()
    count_b = db.query(FormResponse).filter(FormResponse.form_id == form_b.id).count()
    assert count_a == 10
    assert count_b == 20

    # Verify Chat isolation
    chat_a = GroundedChatEngine.process_query("How many responded?", form_a, q, dataset_a["responses"], {}, [])
    chat_b = GroundedChatEngine.process_query("How many responded?", form_b, q, dataset_b["responses"], {}, [])

    assert "10 people responded" in chat_a["content"]
    assert "20 people responded" in chat_b["content"]


# ==============================================================================
# TEST 6 — Permission Failure
# ==============================================================================
def test_6_permission_failure():
    class MockUnauthorizedForm:
        title = "Restricted Form"
        response_access_status = "unauthorized"
        completion_rate = "0%"

    chat_res = GroundedChatEngine.process_query(
        user_message="How many responded to the form?",
        form=MockUnauthorizedForm(),
        questions=[{"question_key": "Q1", "question_text": "Q1"}],
        responses=[],
        analysis_data={},
        chat_history=[]
    )
    assert "The form structure is accessible, but response data is not accessible with the current permissions." in chat_res["content"]


# ==============================================================================
# TEST 7 — Attachment Handling
# ==============================================================================
def test_7_attachment_handling(db_session):
    db, user = db_session

    dataset = {
        "title": "Attachment Survey",
        "questions": [{"question_key": "Q1", "question_text": "Upload Resume", "question_type": "file_upload"}],
        "responses": [],
        "attachments": [
            {
                "file_name": "corrupt_file.xyz",
                "mime_type": "application/octet-stream",
                "drive_file_id": "drv_12345"
            }
        ]
    }
    form = _process_and_save_dataset(dataset, user, db)

    # Verify attachment is tracked in DB
    attachments = db.query(Attachment).filter(Attachment.form_id == form.id).all()
    assert len(attachments) == 1
    assert attachments[0].file_name == "corrupt_file.xyz"
    assert attachments[0].drive_file_id == "drv_12345"
    assert attachments[0].summary is None
