import pytest
from app.services.ingestion.microsoft_connector import MicrosoftConnector
from app.services.cleaning.data_cleaner import DataCleaner
from app.services.analytics.stats_engine import StatsEngine
from app.services.analytics.text_analyzer import TextAnalyzer
from app.services.analytics.comparative_engine import ComparativeEngine
from app.services.chat.grounded_chat import GroundedChatEngine
from app.services.exports.pdf_generator import generate_pdf_report
from app.services.exports.docx_generator import generate_docx_report
from app.services.exports.xlsx_generator import generate_xlsx_workbook
import os

def test_microsoft_forms_demo_dataset():
    dataset = MicrosoftConnector.get_microsoft_forms_demo_dataset()
    assert dataset["source_type"] == "microsoft_form"
    assert "Microsoft 365" in dataset["title"]
    assert len(dataset["questions"]) >= 5
    assert len(dataset["responses"]) >= 20

    # Test DataCleaner on MS Forms dataset
    cleaned_q, cleaned_r, summary = DataCleaner.clean_dataset(dataset["questions"], dataset["responses"])
    assert len(cleaned_q) == len(dataset["questions"])
    assert len(cleaned_r) == len(dataset["responses"])
    assert summary["total_raw_rows"] == len(dataset["responses"])
    assert summary["cleaned_rows"] == len(dataset["responses"])

    # Test StatsEngine on MS Forms
    stats = StatsEngine.calculate_all(cleaned_q, cleaned_r)
    assert stats["basic"]["total_responses"] == len(cleaned_r)
    assert "Q1" in stats["numerical"]
    assert stats["numerical"]["Q1"]["mean"] > 3.0
    assert "Q2" in stats["categorical"]

    # Test TextAnalyzer on MS Forms
    text_analysis = TextAnalyzer.analyze_text_responses(cleaned_q, cleaned_r)
    assert "Q6" in text_analysis

    # Test ComparativeEngine on MS Forms
    comparisons = ComparativeEngine.compare_segments(cleaned_q, cleaned_r)
    assert len(comparisons) > 0

    # Test GroundedChatEngine on MS Forms data
    class MockForm:
        title = dataset["title"]
        description = dataset["description"]
        completion_rate = "100%"
        questions_count = len(cleaned_q)

    analysis_data = {
        "basic_statistics": stats["basic"],
        "numerical_analysis": stats["numerical"],
        "categorical_analysis": stats["categorical"],
        "text_analysis": text_analysis
    }
    
    # 1. Total responses query
    resp1 = GroundedChatEngine.process_query(
        user_message="How many responses were collected in this Microsoft form?",
        form=MockForm(),
        questions=cleaned_q,
        responses=cleaned_r,
        analysis_data=analysis_data,
        chat_history=[]
    )
    assert str(len(cleaned_r)) in resp1["content"]

    # 2. Rating average query
    resp2 = GroundedChatEngine.process_query(
        user_message="What is the average satisfaction score?",
        form=MockForm(),
        questions=cleaned_q,
        responses=cleaned_r,
        analysis_data=analysis_data,
        chat_history=[]
    )
    assert str(round(stats["numerical"]["Q1"]["mean"], 1)) in resp2["content"] or str(stats["numerical"]["Q1"]["mean"]) in resp2["content"]

    # 3. Question breakdown query
    resp3 = GroundedChatEngine.process_query(
        user_message="What are the answers to question 1?",
        form=MockForm(),
        questions=cleaned_q,
        responses=cleaned_r,
        analysis_data=analysis_data,
        chat_history=[]
    )
    assert "Overall Workplace Satisfaction" in resp3["content"]

    # Test Exports for MS Forms
    form_id = "ms-form-test-99"
    ai_insights = {
        "executive_summary": "Microsoft 365 pulse survey shows solid workplace satisfaction.",
        "facts": ["Average satisfaction is 4.4/5", f"Total responses: {len(cleaned_r)}"],
        "interpretations": ["Strong adoption of Teams and OneDrive across squads."],
        "recommendations": ["Optimize meeting loads and streamline review templates."]
    }

    pdf_path = generate_pdf_report(form_id, dataset["title"], dataset["description"], stats, text_analysis, comparisons, ai_insights)
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")

    docx_path = generate_docx_report(form_id, dataset["title"], dataset["description"], stats, text_analysis, comparisons, ai_insights)
    assert os.path.exists(docx_path)
    assert docx_path.endswith(".docx")

    xlsx_path = generate_xlsx_workbook(form_id, dataset["title"], cleaned_q, cleaned_r, stats, ai_insights)
    assert os.path.exists(xlsx_path)
    assert xlsx_path.endswith(".xlsx")

def test_microsoft_forms_question_item_parser():
    # Choice question (multi-select)
    q_choice_multi = {
        "title": "Which tools do you use?",
        "type": "Question.Choice",
        "allowMultipleSelection": True,
        "choices": [{"description": "Teams"}, {"description": "Outlook"}]
    }
    parsed_q1 = MicrosoftConnector._parse_ms_question_item(q_choice_multi, 1)
    assert parsed_q1["question_key"] == "Q1"
    assert parsed_q1["question_type"] == "checkboxes"
    assert parsed_q1["inferred_data_type"] == "multiselect"
    assert "Teams" in parsed_q1["options"]

    # Rating question
    q_rating = {
        "title": "Rate your overall onboarding experience",
        "type": "Question.Rating",
        "maxRating": 5
    }
    parsed_q2 = MicrosoftConnector._parse_ms_question_item(q_rating, 2)
    assert parsed_q2["question_type"] == "rating"
    assert parsed_q2["inferred_data_type"] == "numeric"
    assert parsed_q2["scale_max"] == 5

    # Long text question
    q_text = {
        "title": "Additional suggestions",
        "type": "Question.TextField",
        "isLongText": True
    }
    parsed_q3 = MicrosoftConnector._parse_ms_question_item(q_text, 3)
    assert parsed_q3["question_type"] == "paragraph"
    assert parsed_q3["inferred_data_type"] == "text"
