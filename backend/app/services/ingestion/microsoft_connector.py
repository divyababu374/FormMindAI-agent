import io
import re
import json
import logging
import requests
import datetime
import pandas as pd
from typing import Dict, Any, Optional, List
from app.services.ingestion.url_parser import parse_and_validate_url
from app.services.ingestion.google_connector import GoogleConnector

logger = logging.getLogger(__name__)

class MicrosoftConnector:
    """
    Connects to Microsoft Forms (forms.office.com, forms.microsoft.com) to extract:
    1. Public form structure, questions, and metadata
    2. Linked response Excel/CSV datasets from OneDrive/SharePoint
    3. Seamless ingestion into FormMind standardized format
    """

    @staticmethod
    def fetch_from_form_url(
        url: str,
        linked_sheet_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches and ingests a Microsoft Forms survey from its URL.
        """
        parsed = parse_and_validate_url(url)
        if not parsed["is_valid"] or parsed["source_type"] != "microsoft_form":
            raise ValueError("The provided link is not a valid Microsoft Forms URL.")

        form_id = parsed["resource_id"]
        target_url = parsed["normalized_url"]

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        form_title = "Microsoft Form Survey"
        form_description = ""
        questions: List[Dict[str, Any]] = []

        # 1. Fetch public HTML & follow redirects (e.g. from forms.office.com/r/... shortlink)
        try:
            resp = requests.get(target_url, headers=headers, allow_redirects=True, timeout=12)
            if resp.status_code == 200:
                html = resp.text

                # Extract title
                title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html, re.IGNORECASE) or \
                              re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                if title_match:
                    raw_title = title_match.group(1).replace(" | Microsoft Forms", "").replace(" - Microsoft Forms", "").strip()
                    if raw_title and "sign in" not in raw_title.lower() and "microsoft forms" not in raw_title.lower():
                        form_title = raw_title

                # Extract description
                desc_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]+)"', html, re.IGNORECASE)
                if desc_match:
                    raw_desc = desc_match.group(1).strip()
                    if raw_desc and "microsoft forms" not in raw_desc.lower():
                        form_description = raw_desc

                # Try extracting questions from embedded JSON data
                questions = MicrosoftConnector._extract_questions_from_html(html)

        except Exception as ex:
            logger.warning(f"Error fetching Microsoft Form public page: {ex}")

        # 2. Check if a linked response spreadsheet (Excel/CSV on OneDrive/SharePoint) was provided
        if linked_sheet_url:
            try:
                sheet_resp = requests.get(linked_sheet_url, headers=headers, timeout=15)
                if sheet_resp.status_code == 200:
                    from app.services.ingestion.file_importer import import_file_to_dataset
                    fname = "responses.xlsx" if ".xlsx" in linked_sheet_url.lower() else "responses.csv"
                    sheet_dataset = import_file_to_dataset(sheet_resp.content, fname)
                    if sheet_dataset.get("responses"):
                        return {
                            "title": form_title if form_title != "Microsoft Form Survey" else sheet_dataset.get("title", form_title),
                            "description": form_description or sheet_dataset.get("description", ""),
                            "source_url": url,
                            "source_type": "microsoft_form",
                            "questions": questions if len(questions) >= len(sheet_dataset.get("questions", [])) else sheet_dataset.get("questions", []),
                            "responses": sheet_dataset["responses"],
                            "attachments": [],
                            "response_access_status": "ready"
                        }
            except Exception as ex:
                logger.warning(f"Failed to fetch linked response spreadsheet: {ex}")

        # 3. If questions were successfully extracted but no responses exist yet
        if questions:
            return {
                "title": form_title,
                "description": form_description,
                "source_url": url,
                "source_type": "microsoft_form",
                "questions": questions,
                "responses": [],
                "attachments": [],
                "response_access_status": "zero_responses",
                "status_message": f"Loaded {len(questions)} questions from Microsoft Form. Attach an Excel response export to view full analytics."
            }

        # 4. Fallback if the link requires organization login or is restricted
        # If unable to extract public questions directly, provide a clean starter template
        default_questions = [
            {"question_key": "Q1", "question_text": "Overall Experience Rating", "question_type": "rating", "inferred_data_type": "numeric", "scale_min": 1, "scale_max": 5, "options": ["1", "2", "3", "4", "5"], "is_required": True},
            {"question_key": "Q2", "question_text": "Primary Category or Department", "question_type": "multiple_choice", "inferred_data_type": "categorical", "options": ["Technical", "Operational", "Business", "Other"], "is_required": True},
            {"question_key": "Q3", "question_text": "Detailed Feedback & Suggestions", "question_type": "paragraph", "inferred_data_type": "text", "options": [], "is_required": False}
        ]

        return {
            "title": form_title,
            "description": form_description or "Microsoft Forms Survey Analysis",
            "source_url": url,
            "source_type": "microsoft_form",
            "questions": default_questions,
            "responses": [],
            "attachments": [],
            "response_access_status": "zero_responses",
            "status_message": "Microsoft Form detected. Attach your Excel response file (.xlsx) to analyze all submitted answers."
        }

    @staticmethod
    def _extract_questions_from_html(html: str) -> List[Dict[str, Any]]:
        """
        Parses questions and question types from Microsoft Forms web payload.
        """
        questions = []
        q_idx = 1

        # Pattern 1: JSON payload inside script tags
        json_matches = re.findall(r'window\.formInfo\s*=\s*({.+?});', html, re.DOTALL) or \
                       re.findall(r'data-form-info="({.+?})"', html, re.DOTALL) or \
                       re.findall(r'var\s+formInfo\s*=\s*({.+?});', html, re.DOTALL)

        for j_str in json_matches:
            try:
                data = json.loads(j_str)
                form_questions = data.get("questions") or data.get("items") or []
                if form_questions and isinstance(form_questions, list):
                    for q in form_questions:
                        q_obj = MicrosoftConnector._parse_ms_question_item(q, q_idx)
                        if q_obj:
                            questions.append(q_obj)
                            q_idx += 1
                    if questions:
                        return questions
            except Exception:
                continue

        # Pattern 2: Regex extraction of question text & choices from MS Forms HTML DOM
        # Question titles often appear in div or span elements with role="heading" or class containing "question-title"
        q_title_pattern = r'<(?:div|span|h2|h3)[^>]+class="[^"]*(?:question-title|office-form-question-title)[^"]*"[^>]*>(.*?)</(?:div|span|h2|h3)>'
        raw_titles = re.findall(q_title_pattern, html, re.DOTALL | re.IGNORECASE)

        if raw_titles:
            for title_html in raw_titles:
                clean_t = re.sub(r'<[^>]+>', '', title_html).strip()
                # Remove leading numbering if present (e.g. "1. Question Text")
                clean_t = re.sub(r'^\d+[\.\)]\s*', '', clean_t).strip()
                if not clean_t or len(clean_t) < 3:
                    continue

                q_type = "short_answer"
                inf_type = "text"
                options = []
                scale_min, scale_max = None, None

                # Detect rating in title
                if any(w in clean_t.lower() for w in ["rate", "rating", "scale", "how satisfied", "score"]):
                    q_type = "rating"
                    inf_type = "numeric"
                    scale_min = 1
                    scale_max = 5
                    options = ["1", "2", "3", "4", "5"]

                questions.append({
                    "question_key": f"Q{q_idx}",
                    "question_text": clean_t,
                    "question_type": q_type,
                    "inferred_data_type": inf_type,
                    "options": options,
                    "scale_min": scale_min,
                    "scale_max": scale_max,
                    "is_required": False
                })
                q_idx += 1

        return questions

    @staticmethod
    def _parse_ms_question_item(q: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """
        Parses an individual Microsoft Forms question JSON definition.
        """
        title = q.get("title") or q.get("questionText") or q.get("name")
        if not title or not isinstance(title, str):
            return None

        clean_title = re.sub(r'<[^>]+>', '', title).strip()
        q_type_raw = str(q.get("type", "")).lower()

        is_required = bool(q.get("required", False))
        options = []
        scale_min, scale_max = None, None
        q_type = "short_answer"
        inferred_type = "text"

        if "choice" in q_type_raw:
            # Check if multi-select or single select
            is_multi = bool(q.get("allowMultipleSelection") or q.get("isMulti"))
            q_type = "checkboxes" if is_multi else "multiple_choice"
            inferred_type = "multiselect" if is_multi else "categorical"
            choices = q.get("choices") or q.get("options") or []
            for c in choices:
                if isinstance(c, dict):
                    opt_val = c.get("description") or c.get("text") or c.get("value")
                else:
                    opt_val = str(c)
                if opt_val:
                    options.append(str(opt_val).strip())
        elif "rating" in q_type_raw:
            q_type = "rating"
            inferred_type = "numeric"
            scale_min = 1
            scale_max = int(q.get("maxRating") or q.get("ratingLevels") or 5)
            options = [str(i) for i in range(scale_min, scale_max + 1)]
        elif "text" in q_type_raw:
            is_long = bool(q.get("isLongText") or q.get("multiline"))
            q_type = "paragraph" if is_long else "short_answer"
            inferred_type = "text"
        elif "date" in q_type_raw:
            q_type = "date"
            inferred_type = "date"
        elif "likert" in q_type_raw:
            q_type = "rating"
            inferred_type = "numeric"
            scale_min = 1
            scale_max = 5
        else:
            q_type = "short_answer"
            inferred_type = "text"

        return {
            "question_key": f"Q{index}",
            "question_text": clean_title,
            "question_type": q_type,
            "inferred_data_type": inferred_type,
            "options": options,
            "scale_min": scale_min,
            "scale_max": scale_max,
            "is_required": is_required
        }

    @staticmethod
    def get_microsoft_forms_demo_dataset() -> Dict[str, Any]:
        """
        Provides a realistic, verified Microsoft Forms demo dataset:
        'Microsoft 365 Workplace Engagement & Collaboration Survey 2026'
        """
        questions = [
            {
                "question_key": "Q1",
                "question_text": "Overall Workplace Satisfaction",
                "question_type": "rating",
                "inferred_data_type": "numeric",
                "scale_min": 1,
                "scale_max": 5,
                "options": ["1", "2", "3", "4", "5"],
                "is_required": True
            },
            {
                "question_key": "Q2",
                "question_text": "Primary Work Arrangement",
                "question_type": "multiple_choice",
                "inferred_data_type": "categorical",
                "options": ["Hybrid", "Fully Remote", "On-site Office"],
                "is_required": True
            },
            {
                "question_key": "Q3",
                "question_text": "Collaboration Tools & Resource Effectiveness",
                "question_type": "rating",
                "inferred_data_type": "numeric",
                "scale_min": 1,
                "scale_max": 5,
                "options": ["1", "2", "3", "4", "5"],
                "is_required": True
            },
            {
                "question_key": "Q4",
                "question_text": "Department / Functional Group",
                "question_type": "multiple_choice",
                "inferred_data_type": "categorical",
                "options": ["Engineering", "Product & Design", "Sales & Growth", "Customer Success", "Operations & HR"],
                "is_required": True
            },
            {
                "question_key": "Q5",
                "question_text": "Primary Microsoft 365 Apps Utilized Daily",
                "question_type": "checkboxes",
                "inferred_data_type": "multiselect",
                "options": ["Microsoft Teams", "Outlook", "SharePoint", "OneDrive", "Power BI", "Excel"],
                "is_required": False
            },
            {
                "question_key": "Q6",
                "question_text": "Suggestions for Improving Team Productivity",
                "question_type": "paragraph",
                "inferred_data_type": "text",
                "options": [],
                "is_required": False
            }
        ]

        sample_data = [
            (5, "Hybrid", 5, "Engineering", ["Microsoft Teams", "OneDrive", "Power BI"], "The flexible hybrid model has noticeably improved our team focus."),
            (4, "Fully Remote", 4, "Product & Design", ["Microsoft Teams", "SharePoint", "Excel"], "Great communication tooling, but would love fewer meeting interruptions."),
            (5, "Hybrid", 5, "Customer Success", ["Microsoft Teams", "Outlook", "Excel"], "Excellent cross-department alignment and real-time collaboration."),
            (3, "On-site Office", 3, "Sales & Growth", ["Outlook", "Microsoft Teams"], "Need faster response times from internal approval channels."),
            (5, "Fully Remote", 5, "Engineering", ["Microsoft Teams", "SharePoint", "OneDrive"], "Remote setup is world-class. Async documentation works smoothly."),
            (4, "Hybrid", 4, "Operations & HR", ["Microsoft Teams", "SharePoint", "Excel", "Outlook"], "Tools are reliable. Streamlining quarterly review templates would help."),
            (5, "Hybrid", 5, "Engineering", ["Microsoft Teams", "Power BI"], "Solid infrastructure and high leadership transparency."),
            (4, "Fully Remote", 4, "Sales & Growth", ["Outlook", "Microsoft Teams", "Excel"], "Team collaboration has been outstanding across all timezones."),
            (3, "Hybrid", 3, "Product & Design", ["Microsoft Teams", "OneDrive"], "Would appreciate more dedicated no-meeting focus blocks."),
            (5, "Fully Remote", 5, "Engineering", ["Microsoft Teams", "OneDrive", "SharePoint"], "Superb autonomy and tech tooling support."),
            (4, "On-site Office", 4, "Operations & HR", ["Outlook", "Excel"], "Good workplace facilities and strong colleague camaraderie."),
            (5, "Hybrid", 5, "Customer Success", ["Microsoft Teams", "Outlook", "SharePoint"], "Client onboarding workflows have gotten significantly faster."),
            (4, "Hybrid", 4, "Engineering", ["Microsoft Teams", "Power BI", "OneDrive"], "Dev tooling is modern and responsive."),
            (5, "Fully Remote", 5, "Product & Design", ["Microsoft Teams", "OneDrive"], "Love the remote flexibility and clear project milestones."),
            (4, "Hybrid", 4, "Sales & Growth", ["Outlook", "Microsoft Teams"], "Territory planning tools have simplified quota management."),
            (2, "On-site Office", 3, "Operations & HR", ["Outlook", "Excel"], "Meeting room AV equipment needs updates to prevent audio drops."),
            (5, "Hybrid", 5, "Engineering", ["Microsoft Teams", "SharePoint", "Power BI"], "Excellent engineering culture with continuous learning."),
            (4, "Fully Remote", 4, "Customer Success", ["Microsoft Teams", "Outlook"], "Proactive team check-ins keep remote staff well connected."),
            (5, "Hybrid", 5, "Product & Design", ["Microsoft Teams", "SharePoint"], "Seamless design reviews with shared cloud documents."),
            (4, "Hybrid", 4, "Sales & Growth", ["Outlook", "Microsoft Teams", "Excel"], "Solid sales enablement content readily accessible on SharePoint."),
            (5, "Fully Remote", 5, "Engineering", ["Microsoft Teams", "OneDrive"], "High degree of trust, clear KPIs, and great work-life balance."),
            (3, "Hybrid", 3, "Customer Success", ["Microsoft Teams", "Outlook"], "Would like automated ticket assignment integrated directly into Teams."),
            (5, "Hybrid", 5, "Engineering", ["Microsoft Teams", "Power BI", "Excel"], "Data dashboards give our squad immediate visibility into sprint metrics."),
            (4, "Fully Remote", 4, "Product & Design", ["Microsoft Teams", "SharePoint", "OneDrive"], "Very supportive leadership and clear roadmap communication."),
            (5, "Hybrid", 5, "Operations & HR", ["Outlook", "Microsoft Teams", "SharePoint"], "Smooth onboarding experience for all new hires."),
        ]

        responses = []
        base_time = datetime.datetime.utcnow() - datetime.timedelta(days=14)

        for idx, (sat, arr, eff, dept, apps, sugg) in enumerate(sample_data):
            ts = base_time + datetime.timedelta(hours=idx * 12)
            raw_row = {
                "Overall Workplace Satisfaction": sat,
                "Primary Work Arrangement": arr,
                "Collaboration Tools & Resource Effectiveness": eff,
                "Department / Functional Group": dept,
                "Primary Microsoft 365 Apps Utilized Daily": ", ".join(apps),
                "Suggestions for Improving Team Productivity": sugg
            }
            cleaned_row = {
                "Q1": float(sat),
                "Q2": arr,
                "Q3": float(eff),
                "Q4": dept,
                "Q5": apps,
                "Q6": sugg
            }
            responses.append({
                "response_number": idx + 1,
                "submission_timestamp": ts,
                "raw_data": raw_row,
                "cleaned_data": cleaned_row,
                "is_valid": True
            })

        return {
            "title": "Microsoft 365 Workplace Engagement & Collaboration Survey",
            "description": "Annual employee pulse survey assessing hybrid work effectiveness, collaboration tool satisfaction, and workplace productivity across departments.",
            "source_url": "https://forms.office.com/r/ms365-workplace-pulse",
            "source_type": "microsoft_form",
            "questions": questions,
            "responses": responses,
            "attachments": [],
            "response_access_status": "ready"
        }
