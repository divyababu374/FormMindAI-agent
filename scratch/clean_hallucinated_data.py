import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'backend')


from app.database import SessionLocal
from app.models.form import Form
from app.models.response import FormResponse, ResponseAnswer

from app.models.analysis import FormAnalysis
import datetime

db = SessionLocal()

# Target forms that were created from public google form URL without responses
forms_to_reset = [
    "754ee58e-55be-4271-badc-8b08edbba18b",  # abc
    "d4eac713-5b3f-4159-ab24-d270d513ff0a",  # Learning form
    "7f03201a-d9a1-4944-94af-082cc9c81f79",  # leraning
]

for fid in forms_to_reset:
    form = db.query(Form).filter(Form.id == fid).first()
    if not form:
        continue
    print(f"Resetting form {form.title} ({fid}) to actual original state (0 responses)...")

    # 1. Delete all response answers
    response_ids = [r.id for r in db.query(FormResponse.id).filter(FormResponse.form_id == fid).all()]
    if response_ids:
        deleted_answers = db.query(ResponseAnswer).filter(ResponseAnswer.response_id.in_(response_ids)).delete(synchronize_session=False)
        print(f"  Deleted {deleted_answers} answers")

    # 2. Delete all form responses
    deleted_responses = db.query(FormResponse).filter(FormResponse.form_id == fid).delete(synchronize_session=False)
    print(f"  Deleted {deleted_responses} responses")

    # 3. Reset form columns to truthful state
    form.total_responses_count = 0
    form.completion_rate = "0%"
    form.response_access_status = "unauthorized"
    form.analysis_status = "unavailable"
    form.response_sync_status = "synced"
    form.status_message = "Form questions retrieved, but response data is private. Please attach your linked Google Sheet responses URL or upload the exported responses CSV."
    form.last_synced_at = datetime.datetime.utcnow()

    # 4. Reset form analysis to truthful state
    if form.analysis:
        form.analysis.executive_summary = "This form currently has 0 submitted responses. Attach your linked Google Sheet responses link or upload your exported CSV file to analyze actual submissions."
        form.analysis.basic_statistics = {
            "total_responses": 0,
            "total_questions": form.questions_count,
            "completion_rate": "0%",
            "missing_summary": {}
        }
        form.analysis.numerical_analysis = {}
        form.analysis.categorical_analysis = {}
        form.analysis.text_analysis = {
            "overall_sentiment": {"positive_pct": 0, "neutral_pct": 0, "negative_pct": 0, "compound_score": 0},
            "sentiment_classification": "No responses yet",
            "top_keywords": [],
            "key_themes": [],
            "analyzed_questions": {}
        }
        form.analysis.comparative_analysis = []
        form.analysis.ai_insights = {
            "executive_summary": "This form currently has 0 submitted responses. Attach your linked Google Sheet responses link or upload your exported CSV file to analyze actual submissions.",
            "key_insights": [],
            "actionable_recommendations": [],
            "sentiment_summary": "No submitted responses to analyze."
        }

db.commit()
print("All hallucinated responses purged successfully!")

# Verify current state
all_forms = db.query(Form).all()
for f in all_forms:
    r_count = db.query(FormResponse).filter(FormResponse.form_id == f.id).count()
    print(f"Form: {f.title} | Stored Responses: {r_count} | Access: {f.response_access_status}")

db.close()
