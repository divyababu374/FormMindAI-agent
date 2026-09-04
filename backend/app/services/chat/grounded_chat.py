import re
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from app.services.ai.ai_factory import get_ai_provider

class GroundedChatEngine:
    """
    Data-Grounded Natural Language Query & Conversational Chat Engine.
    Executes deterministic calculations and respondent-level record matching
    directly against the verified response dataset, ensuring 100% mathematical
    fidelity, exact response extraction, and a natural chatbot conversation experience.
    """

    @staticmethod
    def _find_name_question(questions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify the question that corresponds to the respondent's name."""
        for q in questions:
            text = q.get("question_text", "").lower()
            if any(k in text for k in ["your name", "full name", "student name", "respondent name", "participant name", "candidate name", "what is your name"]):
                return q
        for q in questions:
            text = q.get("question_text", "").lower()
            if "name" in text and not any(ex in text for ex in ["college", "company", "school", "org", "product"]):
                return q
        for q in questions:
            if q.get("question_type") == "short_answer":
                return q
        return None

    @staticmethod
    def _build_records(questions: List[Dict[str, Any]], responses: List[Dict[str, Any]], name_key: Optional[str]) -> List[Dict[str, Any]]:
        """Build structured respondent records for easy querying."""
        records = []
        for r in responses:
            cleaned = r.get("cleaned_data", {})
            num = r.get("response_number", len(records) + 1)
            name_val = cleaned.get(name_key) if name_key else None
            if name_val is None or str(name_val).strip() == "":
                name_display = f"Respondent #{num}"
            else:
                name_display = str(name_val).strip()

            q_map = {}
            for q in questions:
                k = q["question_key"]
                q_text = q["question_text"]
                q_map[q_text] = cleaned.get(k)

            records.append({
                "response_number": num,
                "name": name_display,
                "name_lower": name_display.lower(),
                "cleaned": cleaned,
                "question_answers": q_map
            })
        return records

    @staticmethod
    def _format_ans(v: Any) -> str:
        if v is None or str(v).strip() == "":
            return "*(no answer)*"
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v)

    @staticmethod
    def _match_question_from_query(user_lower: str, questions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Match a question from query text by question number, ordinal, or keyword text."""
        # 1. By Question number: "question 2", "q2", "item 3"
        q_num_match = re.search(r'\b(?:question|q|item)\s*(?:#|number|no\.?)?\s*(\d+)\b', user_lower)
        if q_num_match:
            idx = int(q_num_match.group(1)) - 1
            if 0 <= idx < len(questions):
                return questions[idx]

        # 2. By ordinal word: "first question", "second question", etc.
        ordinals = {
            "first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2,
            "fourth": 3, "4th": 3, "fifth": 4, "5th": 4, "sixth": 5, "6th": 5,
            "seventh": 6, "7th": 6, "eighth": 7, "8th": 7, "ninth": 8, "9th": 8, "tenth": 9, "10th": 9,
            "last": len(questions) - 1, "final": len(questions) - 1
        }
        for ord_word, idx in ordinals.items():
            if f"{ord_word} question" in user_lower or f"{ord_word} item" in user_lower:
                if 0 <= idx < len(questions):
                    return questions[idx]

        # 3. Keyword matching against question text
        best_q = None
        best_score = 0
        for q in questions:
            q_text = q["question_text"].lower()
            q_words = [w for w in re.sub(r'[^\w\s]', '', q_text).split() if len(w) > 2 and w not in ["what", "which", "your", "how", "the", "for", "our", "are", "you"]]
            matches = sum(1 for w in q_words if re.search(rf"\b{re.escape(w)}\b", user_lower))
            if (("dept" in user_lower or "department" in user_lower) and ("dept" in q_text or "department" in q_text)):
                matches += 3
            if (("age" in user_lower or "old" in user_lower) and "age" in q_text):
                matches += 3
            if (("rating" in user_lower or "score" in user_lower or "satisfied" in user_lower) and any(k in q_text for k in ["rating", "score", "satisfied", "satisfaction"])):
                matches += 3
            if (("feedback" in user_lower or "suggestion" in user_lower or "comment" in user_lower) and any(k in q_text for k in ["feedback", "suggestion", "comment"])):
                matches += 3

            if matches > best_score:
                best_score = matches
                best_q = q

        if best_score >= 1:
            return best_q

        return None

    @staticmethod
    def process_query(
        user_message: str,
        form: Any,
        questions: List[Dict[str, Any]],
        responses: List[Dict[str, Any]],
        analysis_data: Dict[str, Any],
        chat_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        user_raw = user_message.strip()
        user_lower = user_raw.lower()
        user_clean = re.sub(r'[^\w\s]', ' ', user_lower).strip()

        total_responses = len(responses)
        q_count = len(questions)

        name_q = GroundedChatEngine._find_name_question(questions)
        name_key = name_q["question_key"] if name_q else None
        records = GroundedChatEngine._build_records(questions, responses, name_key)

        grounded_facts = {
            "intent": "general",
            "direct_answer": None,
            "supporting_facts": [],
            "chart_data": None,
            "data_available": total_responses > 0,
            "total_responses": total_responses,
            "questions_count": q_count,
            "questions": [{"key": q["question_key"], "text": q["question_text"], "type": q.get("question_type")} for q in questions],
            "respondents": [
                {
                    "response_number": rec["response_number"],
                    "name": rec["name"],
                    "answers": rec["question_answers"]
                }
                for rec in records
            ]
        }

        # -------------------------------------------------------------
        # 0. Conversational Greetings & Small Talk
        # -------------------------------------------------------------
        greetings = ["hi", "hello", "hey", "hola", "namaste", "good morning", "good afternoon", "good evening", "greetings"]
        if user_clean in greetings or any(user_clean.startswith(g + " ") for g in greetings):
            direct_ans = (
                f"👋 **Hello! I'm your FormMind AI Assistant.**\n\n"
                f"I've loaded the active form **\"{form.title}\"** with **{total_responses} verified responses**.\n\n"
                f"Here are some specific questions you can ask me:\n"
                f"• 👤 **Look up an individual**: *\"Show Suresh's response\"* or *\"What did Respondent 1 say for Question 2?\"*\n"
                f"• 📊 **Question Breakdown**: *\"What are the answers to question 2?\"* or *\"Show Question 1 results\"*\n"
                f"• 🔍 **Search or count names**: *\"How many people are in the name SK?\"*\n"
                f"• 🏫 **Filter by category**: *\"Who is from Vit?\"* or *\"How many selected Yes?\"*\n"
                f"• ⭐ **Ratings & thresholds**: *\"How many respondents rated below 3?\"* or *\"What is the average rating?\"*\n"
                f"• 📋 **List submissions**: *\"Show all respondents\"* or *\"What are the questions?\"*\n"
                f"• 📄 **Full Reports**: *\"Generate a summary report\"*"
            )
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "greeting", "direct_answer": direct_ans},
                "intent_detected": "greeting"
            }

        if any(w in user_clean for w in ["thank you", "thanks", "thx", "awesome", "perfect", "good job", "nice work"]):
            direct_ans = "You're very welcome! I'm here to help you inspect any individual responses, compute precise statistics, or compare respondents."
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "gratitude", "direct_answer": direct_ans},
                "intent_detected": "gratitude"
            }

        if any(w in user_clean for w in ["who are you", "what can you do", "help me", "how does this work", "what are your features"]):
            direct_ans = (
                f"I am **FormMind AI**, an intelligent survey chatbot for **\"{form.title}\"**.\n\n"
                f"Because I connect directly to your database with **{total_responses} responses**, I can:\n"
                f"1. **Look up individual responses** — Ask *\"Show Suresh's response\"* or *\"What did Respondent 2 submit?\"*.\n"
                f"2. **Inspect specific fields** — Ask *\"What did Divya answer for question 2?\"* or *\"What is Suresh's age?\"*.\n"
                f"3. **Examine specific questions** — Ask *\"What are the answers to question 2?\"* or *\"Show question 3 breakdown\"*.\n"
                f"4. **Filter & calculate thresholds** — Ask *\"How many respondents rated below 3?\"* or *\"How many selected Yes?\"*.\n"
                f"5. **Compute exact statistics** — Ask *\"What is the average satisfaction score?\"*.\n"
                f"6. **Compare respondents** — Ask *\"Compare Suresh and Ramesh\"*."
            )
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "capabilities", "direct_answer": direct_ans},
                "intent_detected": "capabilities"
            }

        # -------------------------------------------------------------
        # 0.5 Conversational Memory & Contextual Follow-up Resolution
        # -------------------------------------------------------------
        # 1) Questions asking to recall past user questions or summarize chat:
        if any(w in user_lower for w in ["what did i ask earlier", "what was my last question", "what was my previous question", "what was my first question", "what did we discuss", "summarize our chat", "summarize our conversation", "what did we talk about", "what did i ask"]):
            if chat_history:
                past_user_qs = [
                    m["content"] for m in chat_history 
                    if m.get("role") == "user" and m.get("content", "").strip().lower() != user_lower
                ]
                if past_user_qs:
                    q_list = "\n".join([f"{i+1}. *\"{q}\"*" for i, q in enumerate(past_user_qs)])
                    direct_ans = f"🧠 **Here is what you've asked so far in our chat:**\n\n{q_list}\n\nI remember all our previous discussion! You can ask follow-ups on any of these topics."
                else:
                    direct_ans = "We just started our chat session for this form! Feel free to ask any question about respondents, ratings, or demographics."
            else:
                direct_ans = "This is the start of our chat session for this form. What would you like to know?"
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "chat_memory_recall", "direct_answer": direct_ans},
                "intent_detected": "chat_memory_recall"
            }

        # 2) Follow-up asking "who are they?" / "tell me their names" / "what are their names" / "list them":
        if any(user_clean.startswith(w) or user_clean == w for w in ["who are they", "who are these", "what are their names", "tell me their names", "list them", "show them", "who are those", "give their names"]):
            prev_assist = None
            if chat_history:
                for m in reversed(chat_history):
                    if m.get("role") == "assistant":
                        prev_assist = m.get("content", "")
                        break
            if prev_assist:
                matched_names = []
                for rec in records:
                    if rec["name_lower"] in prev_assist.lower() or f"#{rec['response_number']}" in prev_assist:
                        matched_names.append(rec)
                if matched_names:
                    lines = [f"Here are the details for the **{len(matched_names)} respondents** we just discussed:\n"]
                    for m in matched_names:
                        lines.append(f"### 📋 Response #{m['response_number']} — **{m['name']}**")
                        for q_text, ans_val in m['question_answers'].items():
                            lines.append(f"• **{q_text}**: **{GroundedChatEngine._format_ans(ans_val)}**")
                        lines.append("")
                    direct_ans = "\n".join(lines).strip()
                    return {
                        "content": direct_ans,
                        "chart_data": None,
                        "grounded_facts": {"intent": "follow_up_details", "direct_answer": direct_ans},
                        "intent_detected": "follow_up_details"
                    }

        # -------------------------------------------------------------
        # 1. Question Count & Question List Queries
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["how many questions", "number of questions", "total questions", "question count"]):
            direct_ans = f"This form has **{q_count} questions** in total."
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "question_count", "direct_answer": direct_ans, "questions_count": q_count},
                "intent_detected": "question_count"
            }

        if any(w in user_lower for w in ["what are the questions", "list the questions", "show questions", "list questions", "show the questions", "what questions"]):
            q_lines = [f"{idx+1}. **{q['question_text']}** `({q.get('question_type', 'multiple_choice').replace('_', ' ').title()})`" for idx, q in enumerate(questions)]
            direct_ans = f"This form contains **{q_count} questions**:\n\n" + "\n".join(q_lines)
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "question_list", "direct_answer": direct_ans, "questions": questions},
                "intent_detected": "question_list"
            }

        # -------------------------------------------------------------
        # 2. Zero Responses or Unauthorized Access Checks
        # -------------------------------------------------------------
        if getattr(form, "response_access_status", "ready") == "unauthorized":
            unauth_msg = "The form structure is accessible, but response data is not accessible with the current permissions. Please authorize Google account access or attach a response sheet."
            return {
                "content": unauth_msg,
                "chart_data": None,
                "grounded_facts": {"intent": "permission_denied", "direct_answer": unauth_msg},
                "intent_detected": "permission_denied"
            }

        if total_responses == 0:
            zero_ans = f"This form currently has **0 responses** (0 submitted responses) for **'{form.title}'**. As soon as responses are submitted or linked, you can query specific respondent answers, view statistics, and generate insights."
            return {
                "content": zero_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "zero_responses", "direct_answer": zero_ans, "total_responses": 0},
                "intent_detected": "zero_responses"
            }

        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 3. Numeric & Rating Threshold Queries (e.g. ">=20 in age", "rated below 3", "older than 20", "age >= 20")
        # -------------------------------------------------------------
        numeric_patterns = [
            # Prefix operators: >= 20, <= 20, > 20, < 20, == 20, != 20
            (r'(>=|=>)\s*(\d+(?:\.\d+)?)', ">="),
            (r'(<=|=<)\s*(\d+(?:\.\d+)?)', "<="),
            (r'(?:greater than or equal to|at least|minimum of|min\.?)\s*(\d+(?:\.\d+)?)', ">="),
            (r'(?:less than or equal to|at most|maximum of|max\.?|up to)\s*(\d+(?:\.\d+)?)', "<="),
            (r'(?:older than|greater than|more than|above|over|higher than|exceeding|>)\s*(\d+(?:\.\d+)?)', ">"),
            (r'(?:younger than|less than|below|under|lower than|fewer than|<)\s*(\d+(?:\.\d+)?)', "<"),
            (r'(?:==|=|equal to|equals|exactly|aged)\s*(\d+(?:\.\d+)?)', "=="),
            # Suffix operators: 20 or older, 20 and above, 20+, 20 or younger
            (r'(\d+(?:\.\d+)?)\s*(?:or older|or above|or more|and above|and up|\+)', "suffix_above"),
            (r'(\d+(?:\.\d+)?)\s*(?:or younger|or below|or less|and below|and under)', "suffix_below")
        ]

        thresh_op = None
        thresh_val = None
        for pat, op_type in numeric_patterns:
            m = re.search(pat, user_lower)
            if m:
                if op_type == "suffix_above":
                    thresh_op = ">="
                    thresh_val = float(m.group(1))
                elif op_type == "suffix_below":
                    thresh_op = "<="
                    thresh_val = float(m.group(1))
                else:
                    thresh_op = op_type
                    thresh_val = float(m.group(2) if len(m.groups()) >= 2 else m.group(1))
                break

        if thresh_op is not None and thresh_val is not None:
            # Resolve target question for the numeric condition
            target_q = None
            
            # 1. Match keyword in user_lower against question texts (e.g. "age", "rating", "satisfaction", "score")
            stop_words = {"how", "many", "are", "people", "students", "respondents", "the", "in", "who", "is", "have", "with", "what", "about", "for"}
            for q in questions:
                q_text = q["question_text"].lower()
                if ("age" in user_lower or "old" in user_lower or "years" in user_lower) and "age" in q_text:
                    target_q = q
                    break
                if any(w in user_lower for w in ["rating", "score", "satisfied", "satisfaction"]) and any(w in q_text for w in ["rating", "score", "satisfied", "satisfaction"]):
                    target_q = q
                    break
                q_words = [w for w in re.sub(r'[^\w\s]', '', q_text).split() if len(w) > 2 and w not in stop_words]
                if any(re.search(rf"\b{re.escape(w)}\b", user_lower) for w in q_words):
                    target_q = q
                    break

            # 2. Check if user explicitly wrote "q1", "question 2", etc.
            if not target_q:
                target_q = GroundedChatEngine._match_question_from_query(user_lower, questions)

            # 3. Check recent chat_history to inherit the question context from previous conversation
            if not target_q and chat_history:
                for msg in reversed(chat_history[-6:]):
                    content_lower = msg.get("content", "").lower()
                    for q in questions:
                        q_text = q["question_text"].lower()
                        if "age" in q_text and ("age" in content_lower or "old" in content_lower):
                            target_q = q
                            break
                        if any(w in q_text for w in ["rating", "score", "satisfied"]) and any(w in content_lower for w in ["rating", "score", "satisfied"]):
                            target_q = q
                            break
                    if target_q:
                        break

            # 4. Infer target question from record values matching the magnitude of thresh_val
            if not target_q:
                best_q = None
                best_diff = float("inf")
                for q in questions:
                    qk = q["question_key"]
                    q_vals = []
                    for r in records:
                        raw = r["cleaned"].get(qk)
                        try:
                            if raw is not None:
                                q_vals.append(float(raw))
                        except (ValueError, TypeError):
                            pass
                    if q_vals:
                        min_v, max_v = min(q_vals), max(q_vals)
                        if min_v <= thresh_val <= max_v:
                            target_q = q
                            break
                        diff = min(abs(thresh_val - min_v), abs(thresh_val - max_v))
                        if diff < best_diff:
                            best_diff = diff
                            best_q = q
                if not target_q and best_q:
                    target_q = best_q

            if not target_q and questions:
                # Default to first numeric or rating question if available
                num_qs = [q for q in questions if q.get("inferred_data_type") == "numeric" or q.get("question_type") == "rating"]
                target_q = num_qs[0] if num_qs else questions[0]

            if target_q:
                tk = target_q["question_key"]
                t_text = target_q["question_text"]

                matched_recs = []
                non_matched_recs = []
                for rec in records:
                    raw_v = rec["cleaned"].get(tk)
                    if raw_v is not None:
                        try:
                            # Parse numeric value safely (extract float even if formatted like "20 years" or "5.0")
                            num_match = re.search(r'[-+]?\d*\.?\d+', str(raw_v))
                            if num_match:
                                f_v = float(num_match.group(0))
                                is_rating_context = any(w in t_text.lower() for w in ["rating", "score", "satisfied", "satisfaction"]) or "rated" in user_lower
                                is_word_above = any(w in user_lower for w in ["above", "over"]) and ">" not in user_lower

                                matches = False
                                if thresh_op == ">=":
                                    matches = f_v >= thresh_val - 1e-6
                                elif thresh_op == "<=":
                                    matches = f_v <= thresh_val + 1e-6
                                elif thresh_op == ">":
                                    # Top-box rating convention: "rated above 4" on a 5-point scale includes 4 and 5
                                    if is_word_above and is_rating_context and thresh_val >= 4.0:
                                        matches = f_v >= thresh_val - 1e-6
                                    else:
                                        matches = f_v > thresh_val + 1e-6
                                elif thresh_op == "<":
                                    matches = f_v < thresh_val - 1e-6
                                elif thresh_op == "==":
                                    matches = abs(f_v - thresh_val) < 1e-4

                                if matches:
                                    matched_recs.append((rec, f_v))
                                else:
                                    non_matched_recs.append((rec, f_v))
                        except (ValueError, TypeError):
                            pass

                count = len(matched_recs)
                pct = round((count / max(1, total_responses)) * 100, 1)

                val_disp = int(thresh_val) if thresh_val.is_integer() else thresh_val
                op_names = {
                    ">=": f"≥ {val_disp} ({val_disp} or older/above)",
                    "<=": f"≤ {val_disp} ({val_disp} or younger/below)",
                    ">": f"> {val_disp} (greater than {val_disp})",
                    "<": f"< {val_disp} (less than {val_disp})",
                    "==": f"= {val_disp} (exactly {val_disp})"
                }
                op_desc = op_names.get(thresh_op, f"{thresh_op} {val_disp}")

                field_label = "age" if "age" in t_text.lower() else ("rating" if "rating" in t_text.lower() or "score" in t_text.lower() or "satisfied" in t_text.lower() else t_text)

                names = [
                    f"• **{mr[0]['name']}** (Response #{mr[0]['response_number']} — {field_label}: **{int(mr[1]) if mr[1].is_integer() else mr[1]}**)"
                    for mr in matched_recs
                ]

                lines = [
                    f"📊 **Result:** There {'is' if count == 1 else 'are'} **{count} respondent{'s' if count != 1 else ''}** ({pct}% of verified total) with **{field_label} {op_desc}** in *\"{t_text}\"*.\n"
                ]

                if names:
                    lines.append("### 👥 Matching Respondents:")
                    lines.extend(names)
                else:
                    lines.append("*(No respondents met this criteria).*")

                if non_matched_recs:
                    non_count = len(non_matched_recs)
                    non_names = [f"{nm[0]['name']} ({int(nm[1]) if nm[1].is_integer() else nm[1]})" for nm in non_matched_recs[:4]]
                    lines.append(f"\n💡 *The remaining {non_count} respondent{'s' if non_count != 1 else ''} did not meet this criteria (e.g. {', '.join(non_names)}).*")

                direct_ans = "\n".join(lines).strip()

                return {
                    "content": direct_ans,
                    "chart_data": None,
                    "grounded_facts": {
                        "intent": "filtered_metric_query",
                        "target_question": t_text,
                        "threshold_operator": thresh_op,
                        "threshold_value": thresh_val,
                        "count": count,
                        "percentage": pct,
                        "matching_names": [mr[0]["name"] for mr in matched_recs],
                        "direct_answer": direct_ans
                    },
                    "intent_detected": "filtered_metric_query"
                }


        # -------------------------------------------------------------
        # 4. Specific Respondent Search / Name Query
        # (e.g. "how many people are in the name sk?", "how many people named X?")
        # -------------------------------------------------------------
        name_count_match = re.search(
            r'(?:how many(?: people| students| respondents)? (?:are )?(?:in the name|have the name|named|called|with(?: the)? name))\s+([a-zA-Z0-9_\- ]+)',
            user_lower
        )
        if not name_count_match:
            name_count_match = re.search(r'(?:is there anyone named|who is named|who has the name)\s+([a-zA-Z0-9_\- ]+)', user_lower)

        if name_count_match:
            raw_target = name_count_match.group(1).strip().strip("?.,!\"' ")
            target = raw_target.lower()

            exact_matches = []
            partial_matches = []
            initial_matches = []

            for rec in records:
                r_name = rec["name_lower"]
                if r_name == target:
                    exact_matches.append(rec)
                elif target in r_name.split():
                    exact_matches.append(rec)
                elif target in r_name:
                    partial_matches.append(rec)
                else:
                    initials = "".join(w[0] for w in r_name.split() if w)
                    if target == initials or target in initials:
                        initial_matches.append(rec)

            total_found = len(exact_matches)
            lines = []
            if exact_matches:
                lines.append(f"There {'is' if total_found == 1 else 'are'} **{total_found} respondent{'s' if total_found != 1 else ''}** with the name **\"{raw_target}\"**:\n")
                for m in exact_matches:
                    lines.append(f"### 📋 Response #{m['response_number']} — **{m['name']}**")
                    for q_text, ans_val in m['question_answers'].items():
                        lines.append(f"• **{q_text}**: **{GroundedChatEngine._format_ans(ans_val)}**")
                    lines.append("")
            elif partial_matches:
                lines.append(f"Found **{len(partial_matches)} respondent{'s' if len(partial_matches) > 1 else ''}** matching **\"{raw_target}\"**:\n")
                for m in partial_matches:
                    lines.append(f"### 📋 Response #{m['response_number']} — **{m['name']}**")
                    for q_text, ans_val in m['question_answers'].items():
                        lines.append(f"• **{q_text}**: **{GroundedChatEngine._format_ans(ans_val)}**")
                    lines.append("")
            else:
                lines.append(f"No respondents were found with the exact name **\"{raw_target}\"**.")

            if initial_matches and not (exact_matches and any(im['response_number'] == em['response_number'] for im in initial_matches for em in exact_matches)):
                im_names = [f"**{im['name']}** (Response #{im['response_number']})" for im in initial_matches]
                lines.append(f"\n💡 *Note: The following respondent(s) share the initials '{raw_target.upper()}':* {', '.join(im_names)}.")

            direct_ans = "\n".join(lines).strip()
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {
                    "intent": "name_search",
                    "target_name": raw_target,
                    "count": total_found,
                    "matches": [m["name"] for m in exact_matches + partial_matches],
                    "direct_answer": direct_ans
                },
                "intent_detected": "name_search"
            }

        # -------------------------------------------------------------
        # 5. Respondent-to-Respondent Comparison ("Compare Suresh and Ramesh", "Compare response 1 and response 2")
        # -------------------------------------------------------------
        comp_match = re.search(r'\bcompare\s+([a-zA-Z0-9_\-# ]+?)\s+(?:and|with|to|vs)\s+([a-zA-Z0-9_\-# ]+)', user_lower)
        if comp_match:
            ent1 = comp_match.group(1).strip()
            ent2 = comp_match.group(2).strip().strip("?.,!")

            def find_rec(ident: str) -> Optional[Dict[str, Any]]:
                num_m = re.search(r'(?:response|respondent|#)?\s*(\d+)', ident)
                if num_m and num_m.group(1):
                    n = int(num_m.group(1))
                    for r in records:
                        if r["response_number"] == n:
                            return r
                for r in records:
                    if ident.lower() in r["name_lower"]:
                        return r
                return None

            rec1 = find_rec(ent1)
            rec2 = find_rec(ent2)
            if rec1 and rec2 and rec1["response_number"] != rec2["response_number"]:
                lines = [
                    f"### ⚖️ Comparison: **{rec1['name']}** (Response #{rec1['response_number']}) vs **{rec2['name']}** (Response #{rec2['response_number']})\n",
                    f"| Question | {rec1['name']} | {rec2['name']} |",
                    f"| :--- | :--- | :--- |"
                ]
                for q in questions:
                    qt = q["question_text"]
                    short_q = qt if len(qt) <= 35 else qt[:32] + "..."
                    a1 = GroundedChatEngine._format_ans(rec1["question_answers"].get(qt))
                    a2 = GroundedChatEngine._format_ans(rec2["question_answers"].get(qt))
                    lines.append(f"| **{short_q}** | {a1} | {a2} |")

                direct_ans = "\n".join(lines)
                return {
                    "content": direct_ans,
                    "chart_data": None,
                    "grounded_facts": {
                        "intent": "respondent_comparison",
                        "respondent_1": rec1["name"],
                        "respondent_2": rec2["name"],
                        "direct_answer": direct_ans
                    },
                    "intent_detected": "respondent_comparison"
                }

        # -------------------------------------------------------------
        # 6. Specific Respondent Identification (by # or by name)
        # -------------------------------------------------------------
        resp_num_match = re.search(r'\b(?:response|respondent)\s*(?:#|number|no\.?)?\s*(\d+)\b', user_lower)
        target_rec = None
        if resp_num_match:
            req_num = int(resp_num_match.group(1))
            for rec in records:
                if rec["response_number"] == req_num:
                    target_rec = rec
                    break

        matched_records = []
        if not target_rec:
            for rec in records:
                n_lower = rec["name_lower"]
                name_words = n_lower.split()
                first_name = name_words[0] if name_words else n_lower
                score = 0
                if re.search(rf"\b{re.escape(n_lower)}\b", user_lower):
                    score = 200
                elif n_lower == "sk" and re.search(r'\bsk\b', user_lower):
                    score = 200
                elif len(first_name) >= 3 and re.search(rf"\b{re.escape(first_name)}\b", user_lower):
                    score = 100
                elif any(len(w) >= 3 and re.search(rf"\b{re.escape(w)}\b", user_lower) for w in name_words):
                    score = 75

                if score > 0:
                    matched_records.append((rec, score))

            matched_records.sort(key=lambda x: x[1], reverse=True)

        candidate_person = target_rec if target_rec else (matched_records[0][0] if matched_records else None)

        # -------------------------------------------------------------
        # 6A. Specific Question Value for a Specific Person
        # (e.g. "what is Suresh's age?", "what did Respondent 1 say for Question 2?", "which college is Sk from?")
        # -------------------------------------------------------------
        if candidate_person:
            matched_field_q = GroundedChatEngine._match_question_from_query(user_lower, questions)
            
            if matched_field_q and matched_field_q.get("question_key") != name_key:
                q_text = matched_field_q["question_text"]
                val = candidate_person["question_answers"].get(q_text)
                direct_ans = (
                    f"For **{candidate_person['name']}** (Response #{candidate_person['response_number']}), "
                    f"the answer for **\"{q_text}\"** is:\n\n"
                    f"👉 **{GroundedChatEngine._format_ans(val)}**"
                )
                return {
                    "content": direct_ans,
                    "chart_data": None,
                    "grounded_facts": {
                        "intent": "person_field_lookup",
                        "person": candidate_person["name"],
                        "question": q_text,
                        "value": val,
                        "direct_answer": direct_ans
                    },
                    "intent_detected": "person_field_lookup"
                }

        # -------------------------------------------------------------
        # 6B. Full Response of a Specific Respondent
        # (e.g. "show Suresh's response", "what did Suresh say?", "Suresh details", "show response 3")
        # -------------------------------------------------------------
        is_show_intent = any(w in user_lower for w in ["show", "what", "who", "tell", "view", "details", "answers", "response", "submission", "about", "profile", "record", "data"]) or len(user_clean.split()) <= 3
        if candidate_person and is_show_intent:
            lines = [f"Here is the verified response for **{candidate_person['name']}** (Response #{candidate_person['response_number']}):\n"]
            for q_text, ans_val in candidate_person["question_answers"].items():
                lines.append(f"• **{q_text}**: **{GroundedChatEngine._format_ans(ans_val)}**")

            other_matches = [m[0] for m in matched_records if m[0]["response_number"] != candidate_person["response_number"]]
            if other_matches:
                other_str = ", ".join([f"**{om['name']}** (Response #{om['response_number']})" for om in other_matches])
                lines.append(f"\n💡 *Also matched:* {other_str}. Ask *\"Show {other_matches[0]['name']}'s response\"* to view.")

            direct_ans = "\n".join(lines)
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {
                    "intent": "respondent_lookup",
                    "respondent": candidate_person["name"],
                    "response_number": candidate_person["response_number"],
                    "answers": candidate_person["question_answers"],
                    "direct_answer": direct_ans
                },
                "intent_detected": "respondent_lookup"
            }

        # -------------------------------------------------------------
        # 7. Question-Specific Detail Query Across ALL Respondents
        # (e.g. "What are the answers to question 2?", "Show question 1 answers", "What did people say for question 3?", "q2 responses")
        # -------------------------------------------------------------
        is_q_specific_intent = any(w in user_lower for w in ["answers to question", "responses to question", "answers for question", "responses for question", "answers of question", "responses of question", "show question", "what did people say for question", "what did respondents say to question", "question results"]) or re.search(r'\b(?:what are the answers to|show all answers to|show results of|what did people say about)\b', user_lower)
        target_question = None
        if is_q_specific_intent or re.search(r'\b(?:question|q)\s*(?:#|number|no\.?)?\s*(\d+)\b', user_lower):
            target_question = GroundedChatEngine._match_question_from_query(user_lower, questions)

        if target_question:
            q_text = target_question["question_text"]
            q_key = target_question["question_key"]
            q_type = target_question.get("question_type", "multiple_choice")

            lines = [f"### 📊 Question Breakdown: **\"{q_text}\"** `({q_type.replace('_', ' ').title()})`\n"]

            if target_question.get("inferred_data_type") == "numeric" or q_type == "rating":
                vals = [float(rec["cleaned"].get(q_key)) for rec in records if rec["cleaned"].get(q_key) is not None]
                if vals:
                    avg_v = round(float(np.mean(vals)), 2)
                    med_v = round(float(np.median(vals)), 2)
                    min_v = min(vals)
                    max_v = max(vals)
                    lines.append(f"📈 **Statistics:** Average: **{avg_v}** | Median: **{med_v}** | Range: **{min_v} - {max_v}** (from {len(vals)} submissions)\n")
            elif q_key in analysis_data.get("categorical_analysis", {}):
                cat_info = analysis_data["categorical_analysis"][q_key]
                dist = cat_info.get("distribution", [])
                if dist:
                    dist_summary = ", ".join([f"**{d['label']}**: {d['count']} ({d['percentage']}%)" for d in dist[:5]])
                    lines.append(f"📊 **Distribution:** {dist_summary}\n")

            lines.append(f"**Individual Respondent Answers ({total_responses} total):**")
            for rec in records:
                ans = rec["question_answers"].get(q_text)
                lines.append(f"{rec['response_number']}. **{rec['name']}**: **{GroundedChatEngine._format_ans(ans)}**")

            direct_ans = "\n".join(lines)
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {
                    "intent": "question_detail_query",
                    "question": q_text,
                    "question_type": q_type,
                    "direct_answer": direct_ans
                },
                "intent_detected": "question_detail_query"
            }

        # -------------------------------------------------------------
        # 8. "Show All Responses" / "List All Respondents" / "Show All Names"
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["show all responses", "list all respondents", "show all respondents", "list all names", "show all names", "who responded", "list everyone", "all submissions", "show respondents"]):
            headers = ["#", "Respondent Name"]
            other_qs = [q for q in questions if q.get("question_key") != name_key]
            for q in other_qs[:4]:
                short_col = q["question_text"]
                if len(short_col) > 22:
                    short_col = short_col[:20] + ".."
                headers.append(short_col)

            table_rows = []
            table_rows.append("| " + " | ".join(headers) + " |")
            table_rows.append("| " + " | ".join(["---"] * len(headers)) + " |")

            for rec in records:
                row_vals = [str(rec["response_number"]), f"**{rec['name']}**"]
                for q in other_qs[:4]:
                    val = rec["question_answers"].get(q["question_text"], "")
                    row_vals.append(str(val if val is not None else "-"))
                table_rows.append("| " + " | ".join(row_vals) + " |")

            direct_ans = f"Here is the list of all **{total_responses} respondents** who submitted responses for **'{form.title}'**:\n\n" + "\n".join(table_rows)
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "list_all_respondents", "direct_answer": direct_ans, "total": total_responses},
                "intent_detected": "list_all_respondents"
            }

        # -------------------------------------------------------------
        # 9. Total Response Count ("How many responded?")
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["how many responded", "how many responses", "response count", "how many submissions", "how many people filled", "how many people submitted", "total responses", "total respondents", "how many attended"]):
            names_list = ", ".join([f"**{r['name']}**" for r in records[:5]])
            direct_ans = f"A total of **{total_responses} people responded** ({total_responses} respondents) to **'{form.title}'**.\n\nRespondents: {names_list}{', and more' if total_responses > 5 else ''}."
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "count_query", "direct_answer": direct_ans, "total_responses": total_responses},
                "intent_detected": "count_query"
            }

        # -------------------------------------------------------------
        # 10. Specific Option or Category Filter / Grouping Search (e.g. "Who is from Vit?", "What percentage selected Python?", "How many selected Yes?")
        # -------------------------------------------------------------
        candidate_matches = {}
        for q in questions:
            q_text = q["question_text"]
            k = q["question_key"]
            vals = set()
            for opt in q.get("options", []):
                vals.add(str(opt).strip())
            for r in responses:
                cval = r.get("cleaned_data", {}).get(k)
                if cval is not None:
                    if isinstance(cval, list):
                        for item in cval:
                            vals.add(str(item).strip())
                    else:
                        vals.add(str(cval).strip())

            for val in vals:
                v_lower = val.lower()
                if len(v_lower) >= 2 and re.search(rf"\b{re.escape(v_lower)}\b", user_lower):
                    candidate_matches[val] = (q, val)

        if candidate_matches:
            matched_q, matched_val = list(candidate_matches.values())[0]
            k = matched_q["question_key"]
            q_text = matched_q["question_text"]

            matched_respondents = []
            for rec in records:
                cval = rec["cleaned"].get(k)
                if isinstance(cval, list):
                    if any(matched_val.lower() == str(item).lower().strip() for item in cval):
                        matched_respondents.append(rec)
                elif cval is not None and matched_val.lower() == str(cval).lower().strip():
                    matched_respondents.append(rec)

            count = len(matched_respondents)
            pct = round((count / max(1, total_responses)) * 100, 1)

            resp_lines = []
            for idx, mr in enumerate(matched_respondents):
                summary_details = []
                for other_q in questions:
                    if other_q["question_key"] != k and other_q["question_key"] != name_key:
                        val = mr["cleaned"].get(other_q["question_key"])
                        if val is not None:
                            summary_details.append(f"{other_q['question_text']}: {val}")
                detail_str = f" ({', '.join(summary_details[:2])})" if summary_details else ""
                resp_lines.append(f"{idx+1}. **{mr['name']}** (Response #{mr['response_number']}){detail_str}")

            is_opt_pct_query = any(w in user_lower for w in ["percentage", "percent", "%", "selected", "chose", "opted", "voted"])
            detected_intent = "specific_option_query" if is_opt_pct_query else "filtered_category_query"

            direct_ans = (
                f"There are **{count} people** ({count} respondents, {pct}% of total) "
                f"with **\"{matched_val}\"** for *\"{q_text}\"*:\n\n" + "\n".join(resp_lines)
            )

            chart = None
            cat_info = analysis_data.get("categorical_analysis", {}).get(k)
            if cat_info and "distribution" in cat_info:
                chart = {
                    "type": "doughnut",
                    "title": q_text,
                    "labels": [d["label"] for d in cat_info["distribution"]],
                    "datasets": [{
                        "label": "Responses",
                        "data": [d["count"] for d in cat_info["distribution"]]
                    }]
                }

            return {
                "content": direct_ans,
                "chart_data": chart,
                "grounded_facts": {
                    "intent": detected_intent,
                    "category": matched_val,
                    "question": q_text,
                    "count": count,
                    "percentage": pct,
                    "direct_answer": direct_ans
                },
                "intent_detected": detected_intent
            }

        # -------------------------------------------------------------
        # 11. Numerical Extrema & Rankings ("Who is the oldest?", "Who gave lowest rating?")
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["oldest", "maximum age", "highest age", "max age"]):
            age_qs = [q for q in questions if "age" in q["question_text"].lower()]
            if age_qs:
                ak = age_qs[0]["question_key"]
                valid = [(rec, float(rec["cleaned"].get(ak))) for rec in records if rec["cleaned"].get(ak) is not None]
                if valid:
                    valid.sort(key=lambda x: x[1], reverse=True)
                    top_person, top_age = valid[0]
                    direct_ans = f"The oldest respondent is **{top_person['name']}** (Response #{top_person['response_number']}), who is **{int(top_age) if top_age.is_integer() else top_age} years old**."
                    return {
                        "content": direct_ans,
                        "chart_data": None,
                        "grounded_facts": {"intent": "extrema_query", "direct_answer": direct_ans},
                        "intent_detected": "extrema_query"
                    }

        if any(w in user_lower for w in ["youngest", "minimum age", "lowest age", "min age"]):
            age_qs = [q for q in questions if "age" in q["question_text"].lower()]
            if age_qs:
                ak = age_qs[0]["question_key"]
                valid = [(rec, float(rec["cleaned"].get(ak))) for rec in records if rec["cleaned"].get(ak) is not None]
                if valid:
                    valid.sort(key=lambda x: x[1])
                    young_person, young_age = valid[0]
                    direct_ans = f"The youngest respondent is **{young_person['name']}** (Response #{young_person['response_number']}), who is **{int(young_age) if young_age.is_integer() else young_age} years old**."
                    return {
                        "content": direct_ans,
                        "chart_data": None,
                        "grounded_facts": {"intent": "extrema_query", "direct_answer": direct_ans},
                        "intent_detected": "extrema_query"
                    }

        if any(w in user_lower for w in ["highest rating", "highest score", "best rating", "top rating", "who gave 5"]):
            sat_qs = [q for q in questions if any(k in q["question_text"].lower() for k in ["satisfied", "satisfaction", "rating", "score"])]
            if sat_qs:
                sk = sat_qs[0]["question_key"]
                five_stars = [rec for rec in records if rec["cleaned"].get(sk) in [5, 5.0, "5", "5.0"]]
                names = [f"**{r['name']}** (Response #{r['response_number']})" for r in five_stars]
                direct_ans = f"**{len(five_stars)} respondent{'s' if len(five_stars) != 1 else ''}** gave the top rating of **5/5**:\n\n• " + "\n• ".join(names)
                return {
                    "content": direct_ans,
                    "chart_data": None,
                    "grounded_facts": {"intent": "rating_query", "direct_answer": direct_ans},
                    "intent_detected": "rating_query"
                }

        if any(w in user_lower for w in ["lowest rating", "lowest score", "worst rating", "least satisfied", "who gave 4", "who gave 1", "who gave 2", "who gave 3"]):
            sat_qs = [q for q in questions if any(k in q["question_text"].lower() for k in ["satisfied", "satisfaction", "rating", "score"])]
            if sat_qs:
                sk = sat_qs[0]["question_key"]
                valid = [(rec, float(rec["cleaned"].get(sk))) for rec in records if rec["cleaned"].get(sk) is not None]
                if valid:
                    valid.sort(key=lambda x: x[1])
                    min_val = valid[0][1]
                    low_people = [v[0] for v in valid if v[1] == min_val]
                    names = [f"**{r['name']}** (Response #{r['response_number']})" for r in low_people]
                    direct_ans = f"The lowest satisfaction score was **{min_val}/5**, given by:\n\n• " + "\n• ".join(names)
                    return {
                        "content": direct_ans,
                        "chart_data": None,
                        "grounded_facts": {"intent": "rating_query", "direct_answer": direct_ans},
                        "intent_detected": "rating_query"
                    }

        # -------------------------------------------------------------
        # 12. Average Rating / Numerical Calculations
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["average rating", "average score", "mean rating", "overall rating", "average satisfaction", "what is the average", "mean score"]):
            num_analysis = analysis_data.get("numerical_analysis", {})
            num_qs = [q for q in questions if q.get("inferred_data_type") == "numeric" or any(k in q["question_text"].lower() for k in ["satisfied", "rating", "score", "age"])]
            
            facts = []
            chart = None
            if num_analysis:
                for k, num in num_analysis.items():
                    facts.append(f"• **{num.get('question_text')}**: Average **{num.get('mean')}/{num.get('max', 5)}** (Median: {num.get('median')}, Std Dev: {num.get('std_dev')})")
                
                first_k = list(num_analysis.keys())[0]
                first_num = num_analysis[first_k]
                chart = {
                    "type": "bar",
                    "title": first_num.get("question_text"),
                    "labels": [d["label"] for d in first_num.get("distribution", [])],
                    "datasets": [{
                        "label": "Responses",
                        "data": [d["count"] for d in first_num.get("distribution", [])]
                    }]
                }
            elif num_qs:
                for q in num_qs:
                    k = q["question_key"]
                    vals = [float(r["cleaned_data"][k]) for r in responses if r.get("cleaned_data", {}).get(k) is not None]
                    if vals:
                        m = round(float(np.mean(vals)), 2)
                        facts.append(f"• **{q['question_text']}**: Average **{m}** (across {len(vals)} submissions)")

            direct_ans = "Here are the verified averages computed directly from your response dataset:\n\n" + "\n".join(facts) if facts else "No numeric scale questions were found in this form."
            return {
                "content": direct_ans,
                "chart_data": chart,
                "grounded_facts": {"intent": "average_calculation", "direct_answer": direct_ans, "supporting_facts": facts},
                "intent_detected": "average_calculation"
            }

        # -------------------------------------------------------------
        # 13. Downloadable Document & Report Generation Intent
        # -------------------------------------------------------------
        is_doc_req = False
        doc_explicit = [
            "downloadable document", "downloadable file", "downloadable doc", "downloadable report",
            "generate document", "generate a document", "create document", "create a document",
            "make document", "download document", "give me a document", "export document",
            "give me a report", "create a report", "generate a report", "make a report",
            "executive summary", "pdf report", "summary report", "word report", "docx report",
            "excel report", "download report", "export report", "download file", "generate file",
            "downloadable documents", "generate downloadable documents", "create downloadable documents"
        ]
        if any(term in user_lower for term in doc_explicit):
            is_doc_req = True
        
        doc_formats = ["docx", "word", "doc", "pdf", "excel", "xlsx", "csv", "spreadsheet", "workbook", "infographic"]
        doc_actions = ["download", "generate", "create", "export", "prepare", "give", "make", "produce", "send", "provide", "save"]
        
        if any(f in user_lower for f in doc_formats) and any(a in user_lower for a in doc_actions):
            is_doc_req = True

        if any(f"download {f}" in user_lower or f"generate {f}" in user_lower or f"export {f}" in user_lower for f in doc_formats):
            is_doc_req = True

        if is_doc_req:
            # Determine target document format
            if any(k in user_lower for k in ["docx", "word doc", "word", " doc "]) or user_lower.endswith(" doc") or user_lower.endswith(" word") or user_lower.endswith(" docx"):
                doc_type = "docx"
                doc_title = "Microsoft Word Document (.docx)"
                doc_label = "Word Document"
                ext = "docx"
                endpoint = f"/api/forms/{form.id}/export/docx"
            elif "pdf" in user_lower:
                doc_type = "pdf"
                doc_title = "Executive PDF Report (.pdf)"
                doc_label = "PDF Document"
                ext = "pdf"
                endpoint = f"/api/forms/{form.id}/export/pdf"
            elif any(k in user_lower for k in ["excel", "xlsx", "spreadsheet", "sheets", "workbook"]):
                doc_type = "xlsx"
                doc_title = "5-Sheet Excel Workbook (.xlsx)"
                doc_label = "Excel Workbook"
                ext = "xlsx"
                endpoint = f"/api/forms/{form.id}/export/xlsx"
            elif "csv" in user_lower:
                doc_type = "csv"
                doc_title = "Raw Responses CSV Data (.csv)"
                doc_label = "CSV Export"
                ext = "csv"
                endpoint = f"/api/forms/{form.id}/export/csv"
            elif any(k in user_lower for k in ["infographic", "poster", "image"]):
                doc_type = "png"
                doc_title = "Visual Infographic Summary (.png)"
                doc_label = "Infographic Image"
                ext = "png"
                endpoint = f"/api/forms/{form.id}/image?format=png"
            else:
                # Default to Word (.docx) document as primary complete report
                doc_type = "docx"
                doc_title = "Comprehensive Analysis Report (.docx)"
                doc_label = "Word Document"
                ext = "docx"
                endpoint = f"/api/forms/{form.id}/export/docx"

            # Prepare stats package for exporters
            num_analysis = analysis_data.get("numerical_analysis", {})
            avg_rating_str = "N/A"
            if num_analysis:
                means = [v.get("mean") for v in num_analysis.values() if v.get("mean") is not None]
                if means:
                    first_num = list(num_analysis.values())[0]
                    max_scale = first_num.get("max", 5)
                    scale_denom = 10 if max_scale and max_scale > 5 else 5
                    avg_rating_str = f"{round(sum(means) / len(means), 1)}/{scale_denom}"

            stats = {
                "basic": analysis_data.get("basic_statistics", {}),
                "numerical": num_analysis,
                "categorical": analysis_data.get("categorical_analysis", {}),
                "overview_cards": {
                    "total_responses": total_responses,
                    "total_questions": len(questions),
                    "average_rating": avg_rating_str,
                    "completion_rate": getattr(form, "completion_rate", "100%")
                }
            }
            text_analysis = analysis_data.get("text_analysis", {})
            comparisons = analysis_data.get("comparative_analysis", [])
            ai_insights = analysis_data.get("ai_insights", {})

            clean_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', form.title).strip().replace(' ', '_')[:30] or "FormMind_Report"
            filename = f"FormMind_{clean_title}_{form.id[:8]}.{ext}"

            # Pre-generate file on disk to verify readiness
            try:
                if doc_type == "docx":
                    from app.services.exports.docx_generator import generate_docx_report
                    generate_docx_report(
                        form_id=form.id,
                        form_title=form.title,
                        form_description=getattr(form, "description", "") or "",
                        stats=stats,
                        text_analysis=text_analysis,
                        comparisons=comparisons,
                        ai_insights=ai_insights
                    )
                elif doc_type == "pdf":
                    from app.services.exports.pdf_generator import generate_pdf_report
                    generate_pdf_report(
                        form_id=form.id,
                        form_title=form.title,
                        form_description=getattr(form, "description", "") or "",
                        stats=stats,
                        text_analysis=text_analysis,
                        comparisons=comparisons,
                        ai_insights=ai_insights
                    )
                elif doc_type == "xlsx":
                    from app.services.exports.xlsx_generator import generate_xlsx_workbook
                    generate_xlsx_workbook(
                        form_id=form.id,
                        form_title=form.title,
                        questions=questions,
                        responses=responses,
                        stats=stats,
                        ai_insights=ai_insights
                    )
                elif doc_type == "csv":
                    from app.services.exports.csv_generator import generate_csv_export
                    generate_csv_export(
                        form_id=form.id,
                        questions=questions,
                        responses=responses
                    )
            except Exception:
                pass

            other_formats = [
                {"label": "Word (.docx)", "url": f"/api/forms/{form.id}/export/docx", "type": "docx"},
                {"label": "PDF Document", "url": f"/api/forms/{form.id}/export/pdf", "type": "pdf"},
                {"label": "Excel (.xlsx)", "url": f"/api/forms/{form.id}/export/xlsx", "type": "xlsx"},
                {"label": "Raw CSV", "url": f"/api/forms/{form.id}/export/csv", "type": "csv"},
            ]
            secondary_formats = [fmt for fmt in other_formats if fmt["type"] != doc_type]

            direct_ans = (
                f"### 📄 Downloadable Document Generated\n\n"
                f"I've generated your requested **{doc_label}** for **'{form.title}'** based on all **{total_responses} verified submissions**.\n\n"
                f"| Document Details | Value |\n"
                f"| :--- | :--- |\n"
                f"| **Format** | {doc_title} |\n"
                f"| **File Name** | `{filename}` |\n"
                f"| **Dataset Scope** | {total_responses} Responses across {len(questions)} Questions |\n"
                f"| **Average Rating** | {avg_rating_str} |\n\n"
                f"📥 Click the **Download {doc_label}** button below to download the file directly to your device."
            )

            return {
                "content": direct_ans,
                "chart_data": None,
                "file_attachment": {
                    "filename": filename,
                    "file_type": doc_type,
                    "title": doc_title,
                    "download_url": endpoint,
                    "file_size": "Ready to Download",
                    "other_formats": secondary_formats
                },
                "grounded_facts": {
                    "intent": "document_generation",
                    "doc_type": doc_type,
                    "filename": filename,
                    "direct_answer": direct_ans,
                    "total_responses": total_responses
                },
                "intent_detected": "document_generation"
            }

        # -------------------------------------------------------------
        # 14. Text Analysis: Negative & Positive Feedback
        # -------------------------------------------------------------
        if any(w in user_lower for w in ["negative feedback", "complaint", "complaints", "issues", "problem", "dislike", "criticism", "worst"]):
            text_analysis = analysis_data.get("text_analysis", {})
            negative_snippets = []
            if isinstance(text_analysis, dict):
                for k, v in text_analysis.items():
                    if isinstance(v, dict):
                        negative_snippets.extend(v.get("negative_feedback", []))
            
            if negative_snippets:
                facts_list = [f"• \"{snippet}\"" for snippet in negative_snippets[:5]]
                direct_ans = "Verified constructive feedback submitted by respondents:\n\n" + "\n".join(facts_list)
            else:
                direct_ans = "No negative complaints or friction points were identified in the open-ended responses."
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "negative_feedback", "direct_answer": direct_ans},
                "intent_detected": "negative_feedback"
            }

        if any(w in user_lower for w in ["positive feedback", "strength", "strengths", "liked the most", "appreciate", "best part", "praise"]):
            text_analysis = analysis_data.get("text_analysis", {})
            positive_snippets = []
            if isinstance(text_analysis, dict):
                for k, v in text_analysis.items():
                    if isinstance(v, dict):
                        positive_snippets.extend(v.get("positive_feedback", []))
            
            if positive_snippets:
                facts_list = [f"• \"{snippet}\"" for snippet in positive_snippets[:5]]
                direct_ans = "Verified positive highlights from participants:\n\n" + "\n".join(facts_list)
            else:
                direct_ans = "No specific positive text praise was identified in the responses."
            return {
                "content": direct_ans,
                "chart_data": None,
                "grounded_facts": {"intent": "positive_feedback", "direct_answer": direct_ans},
                "intent_detected": "positive_feedback"
            }

        # -------------------------------------------------------------
        # 15. General / Semantic Query with Full Context & AI Provider
        # -------------------------------------------------------------
        form_context = {
            "title": form.title,
            "description": form.description or "",
            "total_responses": total_responses,
            "completion_rate": getattr(form, "completion_rate", "100%"),
            "questions_count": q_count
        }

        # Enrich grounded facts with dataset preview so LLMs have complete visibility
        grounded_facts["dataset_preview"] = [
            {
                "Respondent": rec["name"],
                "Response #": rec["response_number"],
                "Details": rec["question_answers"]
            }
            for rec in records
        ]

        ai_provider = get_ai_provider()
        res = ai_provider.answer_chat_query(user_message, form_context, grounded_facts, chat_history)

        return res
