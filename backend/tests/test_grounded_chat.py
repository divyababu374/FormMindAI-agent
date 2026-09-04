import pytest
from app.services.chat.grounded_chat import GroundedChatEngine

class MockForm:
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
