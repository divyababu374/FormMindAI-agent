from collections import defaultdict
from typing import Dict, Any, List
import numpy as np

class ComparativeEngine:
    """
    Performs cross-tabulation and comparative segment analysis between categorical and numerical variables.
    """

    @staticmethod
    def compare_segments(questions: List[Dict[str, Any]], responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not responses or len(questions) < 2:
            return []

        categorical_qs = [q for q in questions if q.get("inferred_data_type") == "categorical"]
        numerical_qs = [q for q in questions if q.get("inferred_data_type") == "numeric"]

        comparisons = []

        # Compare categorical groups against numerical ratings
        for cat_q in categorical_qs[:2]:  # Limit to top 2 categorical drivers
            cat_key = cat_q["question_key"]
            cat_text = cat_q["question_text"]
            
            for num_q in numerical_qs[:2]: # Top 2 numerical measures
                num_key = num_q["question_key"]
                num_text = num_q["question_text"]

                # Group values
                grouped_values = defaultdict(list)
                for r in responses:
                    cleaned = r.get("cleaned_data", {})
                    c_val = cleaned.get(cat_key)
                    n_val = cleaned.get(num_key)
                    if c_val is not None and n_val is not None and isinstance(n_val, (int, float)):
                        grouped_values[str(c_val)].append(float(n_val))

                if len(grouped_values) >= 2:
                    segments = []
                    for group_name, vals in grouped_values.items():
                        if len(vals) >= 2:
                            mean_score = round(float(np.mean(vals)), 2)
                            median_score = round(float(np.median(vals)), 2)
                            segments.append({
                                "group": group_name,
                                "count": len(vals),
                                "mean": mean_score,
                                "median": median_score,
                                "percentage_of_total": round((len(vals) / len(responses)) * 100, 1)
                            })

                    # Sort segments by mean score descending
                    segments.sort(key=lambda s: s["mean"], reverse=True)

                    if segments:
                        highest = segments[0]
                        lowest = segments[-1]
                        diff = round(highest["mean"] - lowest["mean"], 2)
                        
                        summary_insight = f"{highest['group']} reported the highest average ({highest['mean']}), while {lowest['group']} averaged {lowest['mean']} (difference: {diff})."

                        comparisons.append({
                            "title": f"{num_text} by {cat_text}",
                            "group_question_key": cat_key,
                            "group_question_text": cat_text,
                            "metric_question_key": num_key,
                            "metric_question_text": num_text,
                            "segments": segments,
                            "key_insight": summary_insight
                        })

        return comparisons
