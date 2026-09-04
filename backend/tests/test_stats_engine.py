import pytest
from app.services.analytics.stats_engine import StatsEngine
from app.services.analytics.comparative_engine import ComparativeEngine

def test_stats_engine_calculations():
    questions = [
        {"question_key": "Q1", "question_text": "Rating", "inferred_data_type": "numeric", "scale_min": 1, "scale_max": 5},
        {"question_key": "Q2", "question_text": "Department", "inferred_data_type": "categorical", "options": ["CS", "IT"]}
    ]
    responses = [
        {"cleaned_data": {"Q1": 5.0, "Q2": "CS"}},
        {"cleaned_data": {"Q1": 4.0, "Q2": "CS"}},
        {"cleaned_data": {"Q1": 3.0, "Q2": "IT"}},
        {"cleaned_data": {"Q1": 4.0, "Q2": "IT"}},
    ]

    stats = StatsEngine.calculate_all(questions, responses)
    assert stats["basic"]["total_responses"] == 4
    assert stats["basic"]["total_questions"] == 2
    assert stats["numerical"]["Q1"]["mean"] == 4.0
    assert stats["numerical"]["Q1"]["median"] == 4.0
    assert stats["numerical"]["Q1"]["min"] == 3.0
    assert stats["numerical"]["Q1"]["max"] == 5.0
    assert stats["categorical"]["Q2"]["count"] == 4

def test_comparative_engine():
    questions = [
        {"question_key": "Q1", "question_text": "Rating", "inferred_data_type": "numeric"},
        {"question_key": "Q2", "question_text": "Department", "inferred_data_type": "categorical"}
    ]
    responses = [
        {"cleaned_data": {"Q1": 5.0, "Q2": "CS"}},
        {"cleaned_data": {"Q1": 5.0, "Q2": "CS"}},
        {"cleaned_data": {"Q1": 3.0, "Q2": "IT"}},
        {"cleaned_data": {"Q1": 3.0, "Q2": "IT"}},
    ]
    comparisons = ComparativeEngine.compare_segments(questions, responses)
    assert len(comparisons) == 1
    segments = comparisons[0]["segments"]
    assert segments[0]["group"] == "CS"
    assert segments[0]["mean"] == 5.0
    assert segments[1]["group"] == "IT"
    assert segments[1]["mean"] == 3.0
