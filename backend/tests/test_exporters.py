import os
# pyrefly: ignore [missing-import]
import pytest
from app.services.exports.pdf_generator import generate_pdf_report
from app.services.exports.docx_generator import generate_docx_report
from app.services.exports.xlsx_generator import generate_xlsx_workbook
from app.services.exports.csv_generator import generate_csv_export
from app.services.exports.infographic_generator import generate_infographic_image

def test_export_file_generation():
    form_id = "test-form-1234"
    title = "Test Survey Analysis"
    desc = "Export testing description"
    
    questions = [
        {"question_key": "Q1", "question_text": "Rating", "inferred_data_type": "numeric", "scale_min": 1, "scale_max": 5},
        {"question_key": "Q2", "question_text": "Department", "inferred_data_type": "categorical", "options": ["CS", "IT"]}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": 5.0, "Q2": "CS"}, "raw_data": {"Rating": "5", "Department": "CS"}},
        {"response_number": 2, "cleaned_data": {"Q1": 4.0, "Q2": "IT"}, "raw_data": {"Rating": "4", "Department": "IT"}},
    ]
    stats = {
        "basic": {"total_responses": 2, "total_questions": 2, "completion_rate": "100%"},
        "numerical": {"Q1": {"question_text": "Rating", "count": 2, "mean": 4.5, "median": 4.5, "std_dev": 0.5, "min": 4.0, "max": 5.0, "distribution": [{"label": "4", "count": 1, "percentage": 50.0}, {"label": "5", "count": 1, "percentage": 50.0}]}},
        "categorical": {"Q2": {"question_text": "Department", "count": 2, "unique_count": 2, "distribution": [{"label": "CS", "count": 1, "percentage": 50.0}, {"label": "IT", "count": 1, "percentage": 50.0}]}},
        "overview_cards": {"total_responses": 2, "total_questions": 2, "average_rating": "4.5/5", "completion_rate": "100%"}
    }
    text_analysis = {}
    comparisons = []
    ai_insights = {
        "executive_summary": "Test summary narrative.",
        "facts": ["Total responses: 2", "Average rating: 4.5/5"],
        "interpretations": ["High satisfaction observed."],
        "recommendations": ["Maintain current quality."]
    }

    # Test PDF
    pdf_path = generate_pdf_report(form_id, title, desc, stats, text_analysis, comparisons, ai_insights)
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")
    assert os.path.getsize(pdf_path) > 1000

    # Test DOCX
    docx_path = generate_docx_report(form_id, title, desc, stats, text_analysis, comparisons, ai_insights)
    assert os.path.exists(docx_path)
    assert docx_path.endswith(".docx")
    assert os.path.getsize(docx_path) > 1000

    # Test XLSX
    xlsx_path = generate_xlsx_workbook(form_id, title, questions, responses, stats, ai_insights)
    assert os.path.exists(xlsx_path)
    assert xlsx_path.endswith(".xlsx")
    assert os.path.getsize(xlsx_path) > 1000

    # Test CSV
    csv_path = generate_csv_export(form_id, questions, responses)
    assert os.path.exists(csv_path)
    assert csv_path.endswith(".csv")

    # Test Infographic PNG
    img_path = generate_infographic_image(form_id, title, stats, ai_insights, file_format="png")
    assert os.path.exists(img_path)
    assert img_path.endswith(".png")
    assert os.path.getsize(img_path) > 10000

def test_pdf_export_with_special_xml_characters():
    # Verify that special characters like &, <, > do not crash ReportLab
    form_id = "test-special-xml"
    title = "Research & Development: Q&A Survey <2026>"
    desc = "Feedback on AI & ML tools for ratings < 5 & > 1"
    
    questions = [
        {"question_key": "Q1", "question_text": "Satisfaction with R&D Tools <Rating>", "inferred_data_type": "numeric", "scale_min": 1, "scale_max": 5}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": 5.0}, "raw_data": {"Satisfaction with R&D Tools <Rating>": "5"}}
    ]
    stats = {
        "basic": {"total_responses": 1, "total_questions": 1, "completion_rate": "100%"},
        "numerical": {"Q1": {"question_text": "Satisfaction with R&D Tools <Rating>", "count": 1, "mean": 5.0, "median": 5.0, "std_dev": 0.0, "min": 5.0, "max": 5.0, "distribution": [{"label": "Score <5>", "count": 1, "percentage": 100.0}]}},
        "categorical": {},
        "overview_cards": {"total_responses": 1, "total_questions": 1, "average_rating": "5.0/5", "completion_rate": "100%"}
    }
    text_analysis = {
        "Q2": {
            "question_text": "Comments & Suggestions",
            "sentiment": {"positive_percentage": 100.0, "negative_percentage": 0.0},
            "positive_feedback": ["Loved the live Q&A session <3!"]
        }
    }
    comparisons = []
    ai_insights = {
        "executive_summary": "Summary with & symbols and <tags>.",
        "facts": ["Fact 1: A & B"],
        "interpretations": ["Interpretation <1>"],
        "recommendations": ["Recommendation: Q&A format"]
    }

    pdf_path = generate_pdf_report(form_id, title, desc, stats, text_analysis, comparisons, ai_insights)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
