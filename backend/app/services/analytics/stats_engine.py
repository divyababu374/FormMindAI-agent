import math
from collections import Counter
from typing import Dict, Any, List
import numpy as np

class StatsEngine:
    """
    High-precision deterministic statistics engine for form response datasets.
    """

    @staticmethod
    def calculate_all(questions: List[Dict[str, Any]], responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes comprehensive statistical analysis across all questions and responses.
        """
        total_responses = len(responses)
        total_questions = len(questions)

        if total_responses == 0:
            return {
                "basic": {
                    "total_responses": 0,
                    "total_questions": total_questions,
                    "completion_rate": "0%",
                    "missing_summary": {}
                },
                "numerical": {},
                "categorical": {},
                "multiselect": {},
                "overview_cards": {
                    "total_responses": 0,
                    "total_questions": total_questions,
                    "average_rating": "N/A",
                    "completion_rate": "0%"
                }
            }

        # Collect response values per question
        q_data = {q["question_key"]: [] for q in questions}
        for r in responses:
            cleaned = r.get("cleaned_data", {})
            for q in questions:
                k = q["question_key"]
                val = cleaned.get(k)
                if val is not None:
                    q_data[k].append(val)

        # Basic Stats
        missing_summary = {}
        total_possible_answers = total_responses * max(1, total_questions)
        total_actual_answers = 0

        for q in questions:
            k = q["question_key"]
            valid_cnt = len(q_data[k])
            missing_cnt = total_responses - valid_cnt
            missing_summary[k] = {
                "question_text": q["question_text"],
                "valid_count": valid_cnt,
                "missing_count": missing_cnt,
                "response_rate_pct": round((valid_cnt / total_responses) * 100, 1)
            }
            total_actual_answers += valid_cnt

        overall_completion_pct = round((total_actual_answers / max(1, total_possible_answers)) * 100, 1)

        numerical_results = {}
        categorical_results = {}
        multiselect_results = {}
        rating_averages = []

        for q in questions:
            k = q["question_key"]
            vals = q_data[k]
            dtype = q.get("inferred_data_type", "text")

            if dtype == "numeric" and vals:
                nums = [float(v) for v in vals if isinstance(v, (int, float))]
                if nums:
                    arr = np.array(nums)
                    mean_val = float(np.mean(arr))
                    median_val = float(np.median(arr))
                    min_val = float(np.min(arr))
                    max_val = float(np.max(arr))
                    std_val = float(np.std(arr)) if len(arr) > 1 else 0.0
                    p25 = float(np.percentile(arr, 25))
                    p75 = float(np.percentile(arr, 75))
                    p90 = float(np.percentile(arr, 90))
                    
                    # Mode
                    c = Counter(nums)
                    mode_val, mode_count = c.most_common(1)[0]
                    
                    # Distribution buckets
                    if max_val <= 10 and min_val >= 0:
                        # Discrete ratings
                        val_counts = Counter([int(round(x)) for x in nums])
                        distribution = []
                        for score in range(int(min_val), int(max_val) + 1):
                            cnt = val_counts.get(score, 0)
                            pct = round((cnt / len(nums)) * 100, 1)
                            distribution.append({"label": str(score), "count": cnt, "percentage": pct})
                    else:
                        # Histogram bins
                        counts, bin_edges = np.histogram(arr, bins=min(5, len(set(nums))))
                        distribution = []
                        for i in range(len(counts)):
                            label = f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}"
                            cnt = int(counts[i])
                            pct = round((cnt / len(nums)) * 100, 1)
                            distribution.append({"label": label, "count": cnt, "percentage": pct})

                    numerical_results[k] = {
                        "question_key": k,
                        "question_text": q["question_text"],
                        "count": len(nums),
                        "mean": round(mean_val, 2),
                        "median": round(median_val, 2),
                        "mode": round(mode_val, 2),
                        "min": round(min_val, 2),
                        "max": round(max_val, 2),
                        "std_dev": round(std_val, 2),
                        "p25": round(p25, 2),
                        "p75": round(p75, 2),
                        "p90": round(p90, 2),
                        "distribution": distribution
                    }

                    if q.get("question_type") in ["rating", "linear_scale"] or max_val <= 10:
                        rating_averages.append((mean_val, max_val))

            elif dtype == "categorical" and vals:
                str_vals = [str(v).strip() for v in vals if str(v).strip()]
                if str_vals:
                    c = Counter(str_vals)
                    total_cnt = len(str_vals)
                    most_common = c.most_common(1)[0]
                    least_common = c.most_common()[-1]
                    
                    distribution = []
                    for opt, count in c.most_common():
                        distribution.append({
                            "label": opt,
                            "count": count,
                            "percentage": round((count / total_cnt) * 100, 1)
                        })

                    categorical_results[k] = {
                        "question_key": k,
                        "question_text": q["question_text"],
                        "count": total_cnt,
                        "unique_count": len(c),
                        "most_common": {"value": most_common[0], "count": most_common[1], "percentage": round((most_common[1] / total_cnt) * 100, 1)},
                        "least_common": {"value": least_common[0], "count": least_common[1], "percentage": round((least_common[1] / total_cnt) * 100, 1)},
                        "distribution": distribution
                    }

            elif dtype == "multiselect" and vals:
                # Array of selections per respondent
                flat_selections = []
                for v in vals:
                    if isinstance(v, list):
                        flat_selections.extend([str(item).strip() for item in v if str(item).strip()])
                    elif isinstance(v, str) and v.strip():
                        flat_selections.append(v.strip())

                if flat_selections:
                    c = Counter(flat_selections)
                    total_selections = len(flat_selections)
                    distribution = []
                    for opt, count in c.most_common():
                        distribution.append({
                            "label": opt,
                            "count": count,
                            "respondent_percentage": round((count / max(1, len(vals))) * 100, 1),
                            "selection_percentage": round((count / total_selections) * 100, 1)
                        })
                    
                    multiselect_results[k] = {
                        "question_key": k,
                        "question_text": q["question_text"],
                        "total_respondents_answered": len(vals),
                        "total_selections_made": total_selections,
                        "distribution": distribution
                    }

        if rating_averages:
            mean_score = round(float(np.mean([m[0] for m in rating_averages])), 1)
            max_scale_found = max(m[1] for m in rating_averages)
            scale_denom = 10 if max_scale_found > 5 else 5
            avg_rating_str = f"{mean_score}/{scale_denom}"
        else:
            avg_rating_str = "N/A"

        return {
            "basic": {
                "total_responses": total_responses,
                "total_questions": total_questions,
                "completion_rate": f"{overall_completion_pct}%",
                "missing_summary": missing_summary
            },
            "numerical": numerical_results,
            "categorical": categorical_results,
            "multiselect": multiselect_results,
            "overview_cards": {
                "total_responses": total_responses,
                "total_questions": total_questions,
                "average_rating": avg_rating_str,
                "completion_rate": f"{overall_completion_pct}%"
            }
        }
