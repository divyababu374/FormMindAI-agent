import pytest
from app.services.cleaning.data_cleaner import DataCleaner

def test_data_cleaning_and_type_detection():
    questions = [
        {"question_key": "Q1", "question_text": "Satisfaction Rating", "question_type": "rating", "inferred_data_type": "numeric", "options": []},
        {"question_key": "Q2", "question_text": "Department", "question_type": "multiple_choice", "inferred_data_type": "categorical", "options": []},
        {"question_key": "Q3", "question_text": "Skills", "question_type": "checkboxes", "inferred_data_type": "multiselect", "options": []}
    ]

    responses = [
        {
            "response_number": 1,
            "raw_data": {"Satisfaction Rating": "5", "Department": "Computer Science", "Skills": "Python, React"},
            "cleaned_data": {"Q1": 5.0, "Q2": "Computer Science", "Q3": ["Python", "React"]}
        },
        {
            "response_number": 2,
            "raw_data": {"Satisfaction Rating": "4", "Department": "Information Tech", "Skills": "React; Cloud"},
            "cleaned_data": {"Q1": 4.0, "Q2": "Information Tech", "Q3": ["React", "Cloud"]}
        },
        # Completely empty row should be dropped
        {
            "response_number": 3,
            "raw_data": {"Satisfaction Rating": "", "Department": "", "Skills": ""},
            "cleaned_data": {}
        }
    ]

    clean_qs, clean_resps, summary = DataCleaner.clean_dataset(questions, responses)
    assert len(clean_resps) == 2
    assert summary["empty_rows_dropped"] == 1
    assert clean_resps[0]["cleaned_data"]["Q1"] == 5.0
    assert isinstance(clean_resps[0]["cleaned_data"]["Q3"], list)
    assert "Python" in clean_resps[0]["cleaned_data"]["Q3"]

def test_numeric_cleaning_with_formatting():
    questions = [
        {"question_key": "Q1", "question_text": "Price Paid", "question_type": "short_answer", "inferred_data_type": "text", "options": []},
        {"question_key": "Q2", "question_text": "Completion Percentage", "question_type": "short_answer", "inferred_data_type": "text", "options": []}
    ]
    responses = [
        {"response_number": 1, "raw_data": {"Price Paid": "$1,200", "Completion Percentage": "95%"}, "cleaned_data": {}},
        {"response_number": 2, "raw_data": {"Price Paid": "$850.50", "Completion Percentage": "100%"}, "cleaned_data": {}}
    ]
    clean_qs, clean_resps, summary = DataCleaner.clean_dataset(questions, responses)
    assert clean_qs[0]["inferred_data_type"] == "numeric"
    assert clean_qs[1]["inferred_data_type"] == "numeric"
    assert clean_resps[0]["cleaned_data"]["Q1"] == 1200.0
    assert clean_resps[0]["cleaned_data"]["Q2"] == 95.0
