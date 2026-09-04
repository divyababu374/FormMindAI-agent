import re
import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np

class DataCleaner:
    """
    Cleans raw form responses, standardizes types, removes empty records,
    and isolates CLEANED DATA from ORIGINAL DATA.
    """

    @staticmethod
    def clean_dataset(questions: List[Dict[str, Any]], responses: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Cleans the question schemas and response records.
        Returns:
          - updated questions (with refined inferred_data_type, scale_min, scale_max, options)
          - cleaned responses (with raw_data preserved and cleaned_data standardized)
          - cleaning_summary (stats on dropped rows, duplicates detected, types inferred)
        """
        if not responses:
            return questions, [], {"total_raw_rows": 0, "cleaned_rows": 0, "empty_rows_dropped": 0, "duplicate_rows_detected": 0}

        total_raw = len(responses)
        valid_responses = []
        seen_fingerprints = set()
        duplicate_count = 0
        empty_count = 0

        # Step 1: Filter empty rows and detect duplicates
        for r in responses:
            raw_dict = r.get("raw_data") or r.get("answers") or {}
            clean_dict = r.get("cleaned_data") or r.get("answers") or {}
            # Check non-empty values excluding Timestamp
            values = [str(v).strip() for k, v in raw_dict.items() if k != "Timestamp" and v is not None and str(v).strip() != ""]
            if not values and clean_dict:
                values = [str(v).strip() for k, v in clean_dict.items() if v is not None and str(v).strip() != ""]
            if not values:
                empty_count += 1
                continue

            # Fingerprint for duplicate check
            fingerprint = "|".join(values)
            if fingerprint in seen_fingerprints:
                duplicate_count += 1
            seen_fingerprints.add(fingerprint)
            valid_responses.append(r)

        # Step 2: Analyze column values across valid responses to refine question types
        q_key_to_values = {q["question_key"]: [] for q in questions}
        for r in valid_responses:
            cleaned = r.get("cleaned_data", {})
            raw = r.get("raw_data", {})
            for q in questions:
                k = q["question_key"]
                raw_text_key = q["question_text"]
                val = cleaned.get(k)
                if val is None and raw_text_key in raw:
                    val = raw.get(raw_text_key)
                if val is not None and str(val).strip() != "":
                    q_key_to_values[k].append(val)

        # Update questions metadata
        for q in questions:
            k = q["question_key"]
            vals = q_key_to_values[k]
            if not vals:
                continue

            # Check if all or most values are numeric
            numeric_vals = []
            for v in vals:
                if isinstance(v, (int, float)):
                    numeric_vals.append(float(v))
                elif isinstance(v, str):
                    try:
                        clean_num_str = v.strip().replace("$", "").replace("%", "").replace(",", "")
                        num = float(clean_num_str)
                        numeric_vals.append(num)
                    except ValueError:
                        pass
            
            if len(numeric_vals) / max(1, len(vals)) >= 0.85:
                q["inferred_data_type"] = "numeric"
                q["scale_min"] = int(np.floor(min(numeric_vals)))
                q["scale_max"] = int(np.ceil(max(numeric_vals)))
                if q["question_type"] not in ["rating", "linear_scale"] and (q["scale_max"] <= 10 and q["scale_min"] >= 0):
                    q["question_type"] = "rating"
            
            # Check multiselect
            elif any(isinstance(v, list) for v in vals):
                q["inferred_data_type"] = "multiselect"
                q["question_type"] = "checkboxes"
                all_opts = set()
                for v in vals:
                    if isinstance(v, list):
                        all_opts.update(v)
                    elif isinstance(v, str):
                        parts = [p.strip() for p in re.split(r'[,;]\s*', v) if p.strip()]
                        all_opts.update(parts)
                q["options"] = sorted(list(all_opts))
                
            # Check categorical
            else:
                str_vals = [str(v).strip() for v in vals if str(v).strip()]
                unique_set = set(str_vals)
                if len(unique_set) <= 12 and len(str_vals) > 0:
                    q["inferred_data_type"] = "categorical"
                    if len(unique_set) <= 3 and unique_set.issubset({"Yes", "No", "Maybe", "yes", "no", "maybe"}):
                        q["question_type"] = "yes_no"
                    elif q["question_type"] not in ["multiple_choice", "dropdown", "yes_no"]:
                        q["question_type"] = "multiple_choice"
                    q["options"] = sorted(list(unique_set))
                else:
                    q["inferred_data_type"] = "text"
                    avg_len = sum(len(s) for s in str_vals) / max(1, len(str_vals))
                    q["question_type"] = "paragraph" if avg_len > 40 else "short_answer"

        # Step 3: Re-clean all response cleaned_data fields to ensure exact type consistency
        standardized_responses = []
        for idx, r in enumerate(valid_responses):
            raw = r.get("raw_data", {})
            cleaned = dict(r.get("cleaned_data", {}))
            
            for q in questions:
                k = q["question_key"]
                raw_text_key = q["question_text"]
                # Look in cleaned first, fallback to raw
                val = cleaned.get(k)
                if val is None and raw_text_key in raw:
                    val = raw.get(raw_text_key)
                if val is None:
                    # Case-insensitive / whitespace-stripped fallback match
                    target_norm = str(raw_text_key).strip().lower()
                    for rk, rv in raw.items():
                        if str(rk).strip().lower() == target_norm:
                            val = rv
                            break

                if val is None or (isinstance(val, str) and val.strip() == ""):
                    cleaned[k] = None
                    continue

                if q["inferred_data_type"] == "numeric":
                    try:
                        if isinstance(val, (int, float)):
                            cleaned[k] = float(val)
                        else:
                            clean_str = str(val).strip().replace("$", "").replace("%", "").replace(",", "")
                            cleaned[k] = float(clean_str)
                    except Exception:
                        cleaned[k] = None
                elif q["inferred_data_type"] == "multiselect":
                    if isinstance(val, list):
                        cleaned[k] = [str(x).strip() for x in val if str(x).strip()]
                    else:
                        cleaned[k] = [p.strip() for p in re.split(r'[,;]\s*', str(val)) if p.strip()]
                elif q["inferred_data_type"] == "categorical":
                    cleaned[k] = str(val).strip()
                else:
                    # Text
                    cleaned[k] = str(val).strip()

            standardized_responses.append({
                "response_number": idx + 1,
                "google_response_id": r.get("google_response_id"),
                "submission_timestamp": r.get("submission_timestamp"),
                "raw_data": raw,
                "cleaned_data": cleaned,
                "is_valid": True
            })


        summary = {
            "total_raw_rows": total_raw,
            "cleaned_rows": len(standardized_responses),
            "empty_rows_dropped": empty_count,
            "duplicate_rows_detected": duplicate_count,
            "total_questions": len(questions)
        }

        return questions, standardized_responses, summary
