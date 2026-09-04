import pytest
from app.services.chat.grounded_chat import GroundedChatEngine

class MockForm:
    id = "test-form-1234-5678"
    title = "Workshop Feedback"
    description = "Test Description"
    completion_rate = "100%"
    questions_count = 2

def test_grounded_chat_specific_option_query():
    questions = [
        {"question_key": "Q1", "question_text": "Favorite Language", "inferred_data_type": "categorical", "options": ["Python", "JavaScript"]},
        {"question_key": "Q2", "question_text": "Rating", "inferred_data_type": "numeric", "options": []}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Python", "Q2": 5.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Python", "Q2": 4.0}},
        {"response_number": 3, "cleaned_data": {"Q1": "JavaScript", "Q2": 3.0}},
        {"response_number": 4, "cleaned_data": {"Q1": "Python", "Q2": 5.0}},
    ]
    analysis_data = {
        "categorical_analysis": {
            "Q1": {"distribution": [{"label": "Python", "count": 3}, {"label": "JavaScript", "count": 1}]}
        }
    }

    # Query about Python percentage
    res = GroundedChatEngine.process_query(
        user_message="What percentage selected Python?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data=analysis_data,
        chat_history=[]
    )

    assert "Python" in res["content"]
    assert "3 respondents" in res["content"] or "75.0%" in res["content"] or "75%" in res["content"]
    assert res["grounded_facts"]["intent"] == "specific_option_query"

def test_grounded_chat_rating_threshold_filters():
    questions = [
        {"question_key": "Q1", "question_text": "Favorite Language", "inferred_data_type": "categorical", "options": ["Python", "JavaScript"]},
        {"question_key": "Q2", "question_text": "Overall Satisfaction", "inferred_data_type": "numeric", "options": []}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Python", "Q2": 5.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Python", "Q2": 4.0}},
        {"response_number": 3, "cleaned_data": {"Q1": "JavaScript", "Q2": 2.0}},
        {"response_number": 4, "cleaned_data": {"Q1": "Python", "Q2": 1.0}},
    ]
    analysis_data = {}

    # Query for rating below 3
    res_low = GroundedChatEngine.process_query(
        user_message="How many respondents rated below 3?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data=analysis_data,
        chat_history=[]
    )
    assert res_low["grounded_facts"]["intent"] == "filtered_metric_query"
    assert "2 respondents" in res_low["content"] or "50%" in res_low["content"]

    # Query for rating above 4
    res_high = GroundedChatEngine.process_query(
        user_message="How many rated above 4?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data=analysis_data,
        chat_history=[]
    )
    assert res_high["grounded_facts"]["intent"] == "filtered_metric_query"
    assert "2 respondents" in res_high["content"] or "50%" in res_high["content"]

def test_grounded_chat_question_breakdown_query():
    questions = [
        {"question_key": "Q1", "question_text": "Participant Name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Favorite Language", "question_type": "multiple_choice", "inferred_data_type": "categorical"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Suresh", "Q2": "Python"}},
        {"response_number": 2, "cleaned_data": {"Q1": "Divya", "Q2": "JavaScript"}},
    ]
    res = GroundedChatEngine.process_query(
        user_message="What are the answers to question 2?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )
    assert res["grounded_facts"]["intent"] == "question_detail_query"
    assert "Favorite Language" in res["content"]
    assert "Suresh" in res["content"]
    assert "Python" in res["content"]
    assert "Divya" in res["content"]
    assert "JavaScript" in res["content"]

def test_grounded_chat_person_field_lookup():
    questions = [
        {"question_key": "Q1", "question_text": "Your Name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Age", "question_type": "short_answer", "inferred_data_type": "numeric"},
        {"question_key": "Q3", "question_text": "College Name", "question_type": "short_answer"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Suresh", "Q2": 24, "Q3": "VIT"}},
        {"response_number": 2, "cleaned_data": {"Q1": "Divya", "Q2": 22, "Q3": "SRM"}},
    ]
    # Check specific field lookup for a person
    res = GroundedChatEngine.process_query(
        user_message="What is Suresh's age?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )
    assert res["grounded_facts"]["intent"] == "person_field_lookup"
    assert "24" in res["content"]
    assert "Suresh" in res["content"]

    # Check question number lookup for a person
    res2 = GroundedChatEngine.process_query(
        user_message="What did Divya answer for question 3?",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )
    assert res2["grounded_facts"]["intent"] == "person_field_lookup"
    assert "SRM" in res2["content"]
    assert "Divya" in res2["content"]

def test_grounded_chat_respondent_comparison():
    questions = [
        {"question_key": "Q1", "question_text": "Your Name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Rating", "question_type": "rating", "inferred_data_type": "numeric"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Suresh", "Q2": 5.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Divya", "Q2": 3.0}},
    ]
    res = GroundedChatEngine.process_query(
        user_message="Compare Suresh and Divya",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )
    assert res["grounded_facts"]["intent"] == "respondent_comparison"
    assert "Suresh" in res["content"]
    assert "Divya" in res["content"]
    assert "5" in res["content"]
    assert "3" in res["content"]


def test_grounded_chat_age_numeric_condition_and_memory_followups():
    questions = [
        {"question_key": "Q1", "question_text": "Your name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Your age", "question_type": "short_answer", "inferred_data_type": "numeric"},
        {"question_key": "Q3", "question_text": "College name", "question_type": "multiple_choice", "options": ["Vit", "Mkjc"]},
        {"question_key": "Q4", "question_text": "Your dept", "question_type": "multiple_choice", "options": ["Cs", "Bcom", "Mtech"]},
        {"question_key": "Q5", "question_text": "How satisfied u are on our product", "question_type": "rating", "inferred_data_type": "numeric"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Divya", "Q2": 20.0, "Q3": "Mkjc", "Q4": "Cs", "Q5": 5.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Divya dharshini", "Q2": 19.0, "Q3": "Vit", "Q4": "Cs", "Q5": 5.0}},
        {"response_number": 3, "cleaned_data": {"Q1": "Suresh Kumar k", "Q2": 20.0, "Q3": "Vit", "Q4": "Cs", "Q5": 5.0}},
        {"response_number": 4, "cleaned_data": {"Q1": "Sk", "Q2": 21.0, "Q3": "Vit", "Q4": "Mtech", "Q5": 5.0}},
        {"response_number": 5, "cleaned_data": {"Q1": "Suresh", "Q2": 24.0, "Q3": "Vit", "Q4": "Bcom", "Q5": 4.0}},
    ]
    history = []

    # 1. Ask "how many are >=20 in age?"
    q1 = "how many are >=20 in age?"
    res1 = GroundedChatEngine.process_query(q1, MockForm(), questions, responses, {}, history)
    assert res1["grounded_facts"]["intent"] == "filtered_metric_query"
    assert res1["grounded_facts"]["count"] == 4
    assert "4 respondents" in res1["content"]
    assert "Divya" in res1["content"]
    assert "Suresh" in res1["content"]
    history.append({"role": "user", "content": q1})
    history.append({"role": "assistant", "content": res1["content"]})

    # 2. Follow-up "who are they?"
    q2 = "who are they?"
    res2 = GroundedChatEngine.process_query(q2, MockForm(), questions, responses, {}, history)
    assert "Divya" in res2["content"]
    assert "Suresh" in res2["content"]
    assert "Response #" in res2["content"]
    history.append({"role": "user", "content": q2})
    history.append({"role": "assistant", "content": res2["content"]})

    # 3. Follow-up "what about < 20?"
    q3 = "what about < 20?"
    res3 = GroundedChatEngine.process_query(q3, MockForm(), questions, responses, {}, history)
    assert res3["grounded_facts"]["intent"] == "filtered_metric_query"
    assert res3["grounded_facts"]["count"] == 1
    assert "Divya dharshini" in res3["content"]
    history.append({"role": "user", "content": q3})
    history.append({"role": "assistant", "content": res3["content"]})

    # 4. General question "what is standard deviation?"
    q4 = "what is standard deviation?"
    res4 = GroundedChatEngine.process_query(q4, MockForm(), questions, responses, {}, history)
    assert "Standard Deviation" in res4["content"]
    assert "mean" in res4["content"].lower()
    history.append({"role": "user", "content": q4})
    history.append({"role": "assistant", "content": res4["content"]})

    # 5. Chat memory question "what was my first question?"
    q5 = "what was my first question?"
    res5 = GroundedChatEngine.process_query(q5, MockForm(), questions, responses, {}, history)
    assert "how many are >=20 in age?" in res5["content"]

def test_grounded_chat_generate_downloadable_docx():
    questions = [
        {"question_key": "Q1", "question_text": "Participant Name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Age", "question_type": "numeric", "inferred_data_type": "numeric"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Divya", "Q2": 20.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Suresh", "Q2": 24.0}}
    ]

    res = GroundedChatEngine.process_query(
        user_message="generate a downloadable docx document as per user requirements",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )

    assert res["intent_detected"] == "document_generation"
    assert res["file_attachment"] is not None
    assert res["file_attachment"]["file_type"] == "docx"
    assert "export/docx" in res["file_attachment"]["download_url"]
    assert "Downloadable Document Generated" in res["content"]
    assert len(res["file_attachment"]["other_formats"]) > 0

def test_grounded_chat_generate_excel_export():
    questions = [
        {"question_key": "Q1", "question_text": "Participant Name", "question_type": "short_answer"},
        {"question_key": "Q2", "question_text": "Age", "question_type": "numeric", "inferred_data_type": "numeric"}
    ]
    responses = [
        {"response_number": 1, "cleaned_data": {"Q1": "Divya", "Q2": 20.0}},
        {"response_number": 2, "cleaned_data": {"Q1": "Suresh", "Q2": 24.0}}
    ]

    res = GroundedChatEngine.process_query(
        user_message="export responses to excel spreadsheet",
        form=MockForm(),
        questions=questions,
        responses=responses,
        analysis_data={},
        chat_history=[]
    )

    assert res["intent_detected"] == "document_generation"
    assert res["file_attachment"] is not None
    assert res["file_attachment"]["file_type"] == "xlsx"
    assert "export/xlsx" in res["file_attachment"]["download_url"]
