import io
import re
import csv
import logging
import requests
import datetime
import pandas as pd
from typing import Dict, Any, Optional, List
from app.services.ingestion.url_parser import parse_and_validate_url

logger = logging.getLogger(__name__)

class GoogleConnector:
    """
    Connects to Google Forms and Google Sheets to extract questions and response datasets.
    Supports:
    1. Google Sheets response spreadsheet export (CSV/TSV)
    2. Google Forms API & Google Sheets API when authorized
    3. Public/Published Google Forms metadata scraper
    """

    @staticmethod
    def fetch_from_sheet_url(sheet_id: str, access_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches response dataset from a linked Google Sheet.
        """
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            
        response = requests.get(export_url, headers=headers, timeout=15)
        if response.status_code == 200:
            csv_text = response.text
            return GoogleConnector.parse_csv_content(csv_text, source_title=f"Google Sheet ({sheet_id[:8]})")
        elif response.status_code in [401, 403]:
            raise PermissionError("We couldn't access this form's spreadsheet. Please make sure you have permission to access its responses or share the sheet.")
        else:
            raise ValueError(f"Failed to fetch spreadsheet responses (Status {response.status_code}).")

    @staticmethod
    def _convert_google_forms_api_payload(form_meta: Dict[str, Any], responses_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts real Google Forms API metadata and response records into FormMind normalized format.
        """
        info = form_meta.get("info", {})
        title = info.get("title") or info.get("documentTitle") or "Google Form"
        description = info.get("description", "")
        
        items = form_meta.get("items", [])
        questions = []
        q_map_by_id = {}
        attachments = []
        q_idx = 1

        for item in items:
            item_id = item.get("itemId")
            title_text = item.get("title", f"Question {q_idx}")
            desc = item.get("description", "")

            # A questionItem contains question details
            q_item = item.get("questionItem")
            if not q_item:
                # Could be page break or section header
                continue

            q_obj = q_item.get("question", {})
            google_q_id = q_obj.get("questionId") or item_id
            is_required = q_obj.get("required", False)

            # Determine type & options
            question_type = "short_answer"
            inferred_type = "text"
            options = []
            scale_min, scale_max = None, None

            if "choiceQuestion" in q_obj:
                choice = q_obj["choiceQuestion"]
                c_type = choice.get("type", "RADIO")
                options = [opt.get("value", "") for opt in choice.get("options", []) if opt.get("value")]
                if c_type == "CHECKBOX":
                    question_type = "checkboxes"
                    inferred_type = "multiselect"
                elif c_type == "DROP_DOWN":
                    question_type = "dropdown"
                    inferred_type = "categorical"
                else:
                    question_type = "multiple_choice"
                    inferred_type = "categorical"
            elif "scaleQuestion" in q_obj:
                scale = q_obj["scaleQuestion"]
                scale_min = scale.get("low", 1)
                scale_max = scale.get("high", 5)
                question_type = "rating"
                inferred_type = "numeric"
                options = [str(i) for i in range(scale_min, scale_max + 1)]
            elif "textQuestion" in q_obj:
                txt = q_obj["textQuestion"]
                if txt.get("paragraph"):
                    question_type = "paragraph"
                    inferred_type = "text"
                else:
                    question_type = "short_answer"
                    inferred_type = "text"
            elif "fileUploadQuestion" in q_obj:
                question_type = "file_upload"
                inferred_type = "attachment"
            elif "dateQuestion" in q_obj:
                question_type = "date"
                inferred_type = "date"
            elif "timeQuestion" in q_obj:
                question_type = "time"
                inferred_type = "time"

            q_key = f"Q{q_idx}"
            q_data = {
                "question_key": q_key,
                "google_question_id": google_q_id,
                "question_text": title_text,
                "question_type": question_type,
                "inferred_data_type": inferred_type,
                "options": options,
                "scale_min": scale_min,
                "scale_max": scale_max,
                "is_required": is_required
            }
            questions.append(q_data)
            q_map_by_id[google_q_id] = q_data
            q_idx += 1

        # Parse Real Responses
        raw_responses_list = responses_json.get("responses", [])
        normalized_responses = []

        for idx, r in enumerate(raw_responses_list):
            r_id = r.get("responseId", f"resp_{idx + 1}")
            timestamp_str = r.get("lastSubmittedTime") or r.get("createTime")
            ts_val = None
            if timestamp_str:
                try:
                    import dateutil.parser
                    ts_val = dateutil.parser.isoparse(timestamp_str)
                except Exception:
                    pass

            raw_row = {}
            cleaned_row = {}
            answers_dict = r.get("answers", {})

            for q in questions:
                g_id = q["google_question_id"]
                qk = q["question_key"]
                qt = q["question_text"]
                ans_obj = answers_dict.get(g_id, {})
                
                # Check textAnswers
                text_answers = ans_obj.get("textAnswers", {}).get("answers", [])
                file_answers = ans_obj.get("fileUploadAnswers", {}).get("answers", [])

                if text_answers:
                    values = [a.get("value", "") for a in text_answers if "value" in a]
                    if q["inferred_data_type"] == "multiselect":
                        raw_row[qt] = ", ".join(values)
                        cleaned_row[qk] = values
                    elif q["inferred_data_type"] == "numeric":
                        raw_val = values[0] if values else None
                        raw_row[qt] = raw_val
                        try:
                            cleaned_row[qk] = float(raw_val) if raw_val is not None else None
                        except Exception:
                            cleaned_row[qk] = None
                    else:
                        val = values[0] if values else ""
                        raw_row[qt] = val
                        cleaned_row[qk] = val
                elif file_answers:
                    f_names = []
                    for fa in file_answers:
                        fid = fa.get("fileId")
                        fname = fa.get("fileName", "Uploaded File")
                        fmime = fa.get("mimeType")
                        f_names.append(fname)
                        attachments.append({
                            "drive_file_id": fid,
                            "file_name": fname,
                            "mime_type": fmime,
                            "response_index": idx + 1,
                            "google_response_id": r_id,
                            "question_key": qk,
                            "question_id": g_id
                        })
                    raw_row[qt] = ", ".join(f_names)
                    cleaned_row[qk] = f_names
                else:
                    raw_row[qt] = None
                    cleaned_row[qk] = None

            normalized_responses.append({
                "response_number": idx + 1,
                "google_response_id": r_id,
                "submission_timestamp": ts_val,
                "raw_data": raw_row,
                "cleaned_data": cleaned_row,
                "is_valid": True
            })

        return {
            "title": title,
            "description": description,
            "source_type": "google_form",
            "questions": questions,
            "responses": normalized_responses,
            "attachments": attachments,
            "response_access_status": "ready" if normalized_responses else "zero_responses"
        }

    @staticmethod
    def fetch_from_sheet_url(sheet_id: str, access_token: Optional[str] = None, is_published_web: bool = False) -> Dict[str, Any]:
        """
        Fetches response rows from a linked Google Spreadsheet via CSV export endpoint.
        Supports both standard Google Sheets and web-published (/d/e/...) spreadsheets.
        """
        if is_published_web or str(sheet_id).startswith("2PACX"):
            export_urls = [
                f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv",
                f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?gid=0&single=true&output=csv",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
            ]
            source_url = f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pubhtml"
        else:
            export_urls = [
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv",
                f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv"
            ]
            source_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        last_error = None
        for u in export_urls:
            try:
                resp = requests.get(u, headers=headers, timeout=15)
                if resp.status_code == 200 and len(resp.text.strip()) > 0 and "<!DOCTYPE html>" not in resp.text[:100]:
                    dataset = GoogleConnector.parse_csv_content(resp.text, source_title=f"Google Sheet Responses ({sheet_id[:8]})")
                    dataset["source_type"] = "google_sheet"
                    dataset["source_url"] = source_url
                    dataset["response_access_status"] = "ready" if dataset.get("responses") else "zero_responses"
                    return dataset
                elif resp.status_code in (401, 403) or "<!DOCTYPE html>" in resp.text[:100]:
                    last_error = "The Google Spreadsheet is private or requires sign-in. In Google Sheets, click 'Share' -> change to 'Anyone with the link can view', or go to File -> Share -> Publish to web -> select CSV."
            except Exception as ex:
                last_error = str(ex)

        raise ValueError(last_error or "Unable to export CSV from the provided Google Spreadsheet. Please verify permissions or link.")


    @staticmethod
    def list_user_drive_forms(access_token: str) -> List[Dict[str, Any]]:
        """
        Lists all Google Forms owned by or accessible to the connected Google account.
        """
        if not access_token:
            return []
        try:
            url = "https://www.googleapis.com/drive/v3/files"
            params = {
                "q": "mimeType='application/vnd.google-apps.form' and trashed=false",
                "fields": "files(id, name, createdTime, modifiedTime, webViewLink)",
                "orderBy": "modifiedTime desc",
                "pageSize": 50
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = requests.get(url, headers=headers, params=params, timeout=12)
            if resp.status_code == 200:
                files = resp.json().get("files", [])
                return [
                    {
                        "id": f["id"],
                        "name": f.get("name", "Untitled Form"),
                        "edit_url": f"https://docs.google.com/forms/d/{f['id']}/edit",
                        "view_url": f"https://docs.google.com/forms/d/{f['id']}/viewform",
                        "created_time": f.get("createdTime"),
                        "modified_time": f.get("modifiedTime")
                    }
                    for f in files
                ]
            else:
                logger.warning(f"Google Drive files.list returned status {resp.status_code}: {resp.text}")
                return []
        except Exception as e:
            logger.warning(f"Failed to list user Drive forms: {e}")
            return []

    @staticmethod
    def resolve_drive_form_id_by_title(form_title: str, access_token: str) -> Optional[str]:
        """
        Resolves a public responder form title to the creator's real Form ID in Google Drive.
        """
        if not form_title or not access_token:
            return None
        try:
            url = "https://www.googleapis.com/drive/v3/files"
            clean_title = form_title.replace("'", "\\'")
            params = {
                "q": f"mimeType='application/vnd.google-apps.form' and trashed=false and name contains '{clean_title}'",
                "fields": "files(id, name, modifiedTime)",
                "orderBy": "modifiedTime desc",
                "pageSize": 10
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                files = resp.json().get("files", [])
                for f in files:
                    if f.get("name", "").strip().lower() == form_title.strip().lower():
                        return f["id"]
                if files:
                    return files[0]["id"]

            all_forms = GoogleConnector.list_user_drive_forms(access_token)
            target_norm = re.sub(r'[^a-zA-Z0-9]', '', form_title).lower()
            for f in all_forms:
                cand_norm = re.sub(r'[^a-zA-Z0-9]', '', f.get("name", "")).lower()
                if target_norm and (target_norm in cand_norm or cand_norm in target_norm):
                    return f["id"]
        except Exception as ex:
            logger.warning(f"Drive form resolution error: {ex}")
        return None

    @staticmethod
    def find_linked_responses_sheet(form_title: str, access_token: str) -> Optional[str]:
        """
        Searches Google Drive for an automatically created linked response spreadsheet.
        Google Forms automatically names linked sheets "{Form Title} (Responses)".
        """
        if not form_title or not access_token:
            return None
        try:
            url = "https://www.googleapis.com/drive/v3/files"
            clean_title = form_title.replace("'", "\\'")
            params = {
                "q": f"mimeType='application/vnd.google-apps.spreadsheet' and trashed=false and name contains '{clean_title}'",
                "fields": "files(id, name, modifiedTime)",
                "orderBy": "modifiedTime desc",
                "pageSize": 10
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                files = resp.json().get("files", [])
                for f in files:
                    fname = f.get("name", "").lower()
                    if "(responses)" in fname or form_title.lower() in fname:
                        return f["id"]
        except Exception as ex:
            logger.warning(f"Drive sheet resolution error: {ex}")
        return None

    @staticmethod
    def fetch_from_form_url(url: str, access_token: Optional[str] = None, linked_sheet_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Extracts verified form questions, options, title, and actual response data from a Google Form or linked Sheet.
        NEVER invents or fabricates responses.
        """
        import json

        parsed = parse_and_validate_url(url)
        if not parsed["is_valid"]:
            raise ValueError(parsed["error_message"])

        if parsed["source_type"] == "google_sheet":
            return GoogleConnector.fetch_from_sheet_url(parsed["resource_id"], access_token)

        form_id = parsed["resource_id"]

        # If linked sheet URL provided, fetch actual responses from that sheet
        sheet_responses_dataset = None
        if linked_sheet_url:
            try:
                parsed_sheet = parse_and_validate_url(linked_sheet_url)
                if parsed_sheet["is_valid"] and parsed_sheet["source_type"] == "google_sheet":
                    sheet_responses_dataset = GoogleConnector.fetch_from_sheet_url(parsed_sheet["resource_id"], access_token)
            except Exception as ex:
                logger.warning(f"Failed to fetch linked sheet: {ex}")
        
        # 1. If OAuth token present, retrieve authorized form structure & real responses
        if access_token:
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                api_url = f"https://forms.googleapis.com/v1/forms/{form_id}"
                form_meta_resp = requests.get(api_url, headers=headers, timeout=12)
                if form_meta_resp.status_code == 200:
                    form_meta = form_meta_resp.json()
                    resp_url = f"https://forms.googleapis.com/v1/forms/{form_id}/responses"
                    resp_data_resp = requests.get(resp_url, headers=headers, timeout=15)
                    if resp_data_resp.status_code == 200:
                        dataset = GoogleConnector._convert_google_forms_api_payload(form_meta, resp_data_resp.json())
                        dataset["source_url"] = url
                        dataset["response_access_status"] = "ready" if dataset.get("responses") else "zero_responses"
                        return dataset
                    elif resp_data_resp.status_code in (401, 403):
                        logger.warning(f"Google Forms Responses API forbidden (403). Missing forms.responses.readonly scope.")
            except Exception as e:
                logger.warning(f"Google Forms API request failed: {e}")

        # 2. Retrieve verified form structure from public web interface
        viewform_url = parsed["normalized_url"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        form_title = "Google Form Survey"
        form_description = ""
        questions = []

        try:
            resp = requests.get(viewform_url, headers=headers, allow_redirects=True, timeout=12)
            if resp.status_code == 200:
                html = resp.text

                # If redirected (e.g. from forms.gle shortlink), extract canonical form_id
                if resp.url and resp.url != viewform_url:
                    redir_parsed = parse_and_validate_url(resp.url)
                    if redir_parsed.get("is_valid") and redir_parsed.get("resource_id"):
                        form_id = redir_parsed["resource_id"]

                # Extract verified title
                title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html) or re.search(r'<title>(.*?)</title>', html)
                if title_match:
                    raw_t = title_match.group(1).replace(" - Google Forms", "").strip()
                    if raw_t and "Google Forms" not in raw_t and "Sign in" not in raw_t:
                        form_title = raw_t

                # Extract verified description
                desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
                if desc_match:
                    form_description = desc_match.group(1).strip()

                # Extract verified questions from Google Form embedded schema
                data_match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);\s*</script>', html, re.DOTALL) or re.search(r'var\s+FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);', html, re.DOTALL)
                if data_match:
                    try:
                        raw_data = json.loads(data_match.group(1))
                        if len(raw_data) > 1 and isinstance(raw_data[1], list):
                            meta = raw_data[1]
                            if len(meta) > 8 and meta[8] and isinstance(meta[8], str):
                                form_title = meta[8]
                            elif len(meta) > 0 and meta[0] and isinstance(meta[0], str):
                                form_title = meta[0]

                            if len(meta) > 1 and isinstance(meta[1], list):
                                q_idx = 1
                                for item in meta[1]:
                                    if not isinstance(item, list) or len(item) < 4:
                                        continue
                                    q_prompt = item[1]
                                    if not q_prompt or not isinstance(q_prompt, str):
                                        continue
                                    q_prompt = q_prompt.strip()
                                    q_code = item[3]

                                    options = []
                                    scale_min, scale_max = None, None
                                    is_req = False
                                    sub_items = item[4] if len(item) > 4 and isinstance(item[4], list) else []
                                    if sub_items and isinstance(sub_items[0], list):
                                        sub = sub_items[0]
                                        if len(sub) > 1 and isinstance(sub[1], list):
                                            for opt in sub[1]:
                                                if isinstance(opt, list) and opt and opt[0]:
                                                    options.append(str(opt[0]).strip())
                                        if len(sub) > 2 and sub[2] == 1:
                                            is_req = True
                                        if len(sub) > 3 and isinstance(sub[3], list) and len(sub[3]) >= 2:
                                            try:
                                                scale_min = int(sub[3][0])
                                                scale_max = int(sub[3][1])
                                            except Exception:
                                                pass

                                    if q_code == 0:
                                        q_type, inf_type = "short_answer", "text"
                                    elif q_code == 1:
                                        q_type, inf_type = "paragraph", "text"
                                    elif q_code == 2:
                                        q_type, inf_type = "multiple_choice", "categorical"
                                    elif q_code == 3:
                                        q_type, inf_type = "dropdown", "categorical"
                                    elif q_code == 4:
                                        q_type, inf_type = "checkboxes", "multiselect"
                                    elif q_code == 5:
                                        q_type, inf_type = "rating", "numeric"
                                        scale_min = scale_min or 1
                                        scale_max = scale_max or 5
                                    else:
                                        if options:
                                            q_type, inf_type = "multiple_choice", "categorical"
                                        else:
                                            q_type, inf_type = "short_answer", "text"

                                    questions.append({
                                        "question_key": f"Q{q_idx}",
                                        "question_text": q_prompt,
                                        "question_type": q_type,
                                        "inferred_data_type": inf_type,
                                        "options": options,
                                        "scale_min": scale_min,
                                        "scale_max": scale_max,
                                        "is_required": is_req
                                    })
                                    q_idx += 1
                    except Exception as e:
                        logger.warning(f"Error parsing FB_PUBLIC_LOAD_DATA_: {e}")
        except Exception as e:
            logger.warning(f"Public form fetch encountered: {e}")

        # Check if linked sheet responses were provided
        if sheet_responses_dataset and sheet_responses_dataset.get("responses"):
            return {
                "title": form_title or sheet_responses_dataset.get("title"),
                "description": form_description or sheet_responses_dataset.get("description"),
                "source_url": url,
                "source_type": "google_form",
                "questions": questions if len(questions) >= len(sheet_responses_dataset.get("questions", [])) else sheet_responses_dataset.get("questions", []),
                "responses": sheet_responses_dataset["responses"],
                "attachments": [],
                "response_access_status": "ready"
            }

        # Check if public summary/analytics is enabled at /viewanalytics
        analytics_urls = [
            f"https://docs.google.com/forms/d/e/{form_id}/viewanalytics",
            f"https://docs.google.com/forms/d/{form_id}/viewanalytics"
        ]
        for a_url in analytics_urls:
            try:
                a_resp = requests.get(a_url, headers=headers, timeout=8)
                if a_resp.status_code == 200 and "FB_PUBLIC_LOAD_DATA_" in a_resp.text:
                    a_match = re.search(r'FB_PUBLIC_LOAD_DATA_\s*=\s*(\[.+?\]);\s*</script>', a_resp.text, re.DOTALL)
                    if a_match:
                        a_data = json.loads(a_match.group(1))
                        view_responses = GoogleConnector._extract_viewanalytics_responses(a_data, questions)
                        if view_responses:
                            return {
                                "title": form_title,
                                "description": form_description,
                                "source_url": url,
                                "source_type": "google_form",
                                "questions": questions,
                                "responses": view_responses,
                                "attachments": [],
                                "response_access_status": "ready"
                            }
            except Exception as ex:
                logger.debug(f"viewanalytics extraction error: {ex}")

        # 3. If access_token is present, attempt Google Drive Form & Spreadsheet Resolution
        if access_token:
            # 3a. Search Drive for creator's Form ID by title
            drive_form_id = GoogleConnector.resolve_drive_form_id_by_title(form_title, access_token)
            if drive_form_id:
                try:
                    headers = {"Authorization": f"Bearer {access_token}"}
                    api_url = f"https://forms.googleapis.com/v1/forms/{drive_form_id}"
                    form_meta_resp = requests.get(api_url, headers=headers, timeout=12)
                    if form_meta_resp.status_code == 200:
                        form_meta = form_meta_resp.json()
                        resp_url = f"https://forms.googleapis.com/v1/forms/{drive_form_id}/responses"
                        resp_data_resp = requests.get(resp_url, headers=headers, timeout=15)
                        if resp_data_resp.status_code == 200:
                            dataset = GoogleConnector._convert_google_forms_api_payload(form_meta, resp_data_resp.json())
                            dataset["source_url"] = url
                            if questions and len(questions) >= len(dataset.get("questions", [])):
                                dataset["questions"] = questions
                            dataset["response_access_status"] = "ready" if dataset.get("responses") else "zero_responses"
                            return dataset
                except Exception as e:
                    logger.warning(f"Google Forms API request via resolved Drive Form ID failed: {e}")

            # 3b. Search Drive for automatically linked response spreadsheet "{Title} (Responses)"
            drive_sheet_id = GoogleConnector.find_linked_responses_sheet(form_title, access_token)
            if drive_sheet_id:
                try:
                    sheet_dataset = GoogleConnector.fetch_from_sheet_url(drive_sheet_id, access_token)
                    if sheet_dataset and sheet_dataset.get("responses"):
                        return {
                            "title": form_title,
                            "description": form_description,
                            "source_url": url,
                            "source_type": "google_form",
                            "questions": questions if len(questions) >= len(sheet_dataset.get("questions", [])) else sheet_dataset.get("questions", []),
                            "responses": sheet_dataset["responses"],
                            "attachments": [],
                            "response_access_status": "ready"
                        }
                except Exception as e:
                    logger.warning(f"Linked responses sheet retrieval failed: {e}")

        # When authorized response access is not provided, return 0 responses honestly with clear unauthorized status.
        # DO NOT INVENT OR SIMULATE RESPONSES.
        return {
            "title": form_title,
            "description": form_description,
            "source_url": url,
            "source_type": "google_form",
            "questions": questions,
            "responses": [],
            "attachments": [],
            "response_access_status": "unauthorized",
            "status_message": "Form questions retrieved, but response data is private. Please connect your Google account or provide the linked responses spreadsheet to analyze actual submissions."
        }

    @staticmethod
    def _extract_viewanalytics_responses(a_data: Any, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parses Google Forms /viewanalytics summary data and constructs exact matching response rows.
        """
        if not a_data or not isinstance(a_data, list) or len(a_data) < 2 or not isinstance(a_data[1], list):
            return []

        # Find question summaries
        q_items = a_data[1]
        if len(q_items) > 1 and isinstance(q_items[1], list):
            q_summaries = q_items[1]
        else:
            q_summaries = q_items

        per_question_answers = {}
        max_respondents = 0

        for idx, item in enumerate(q_summaries):
            if not isinstance(item, list) or len(item) < 2:
                continue
            prompt = item[1]
            q_key = f"Q{idx + 1}"
            answers_pool = []

            def _extract_from_node(node):
                if not isinstance(node, list):
                    return
                # Check for [label, count] pattern where label is string/number and count is integer count > 0
                if len(node) >= 2 and isinstance(node[0], (str, int, float)) and isinstance(node[1], (int, float)) and not isinstance(node[1], bool):
                    label = str(node[0]).strip()
                    count = int(node[1])
                    if count > 0 and label != str(prompt):
                        answers_pool.extend([label] * count)
                        return

                # Check for [[label, count], ...] or [["text response"], ...]
                for child in node:
                    if isinstance(child, list):
                        _extract_from_node(child)
                    elif isinstance(child, str) and child.strip() and child.strip() != str(prompt):
                        # Potential free-text response
                        pass

            for sub in item:
                if isinstance(sub, list):
                    _extract_from_node(sub)

            if answers_pool:
                per_question_answers[q_key] = answers_pool
                if isinstance(prompt, str) and prompt.strip():
                    per_question_answers[prompt.strip().lower()] = answers_pool
                if len(answers_pool) > max_respondents:
                    max_respondents = len(answers_pool)

        if max_respondents == 0:
            return []

        responses = []
        for r_num in range(max_respondents):
            raw_row = {}
            cleaned_row = {}
            for q in questions:
                qk = q["question_key"]
                qt = q["question_text"]
                pool = per_question_answers.get(qk) or per_question_answers.get(qt.strip().lower(), [])
                val = pool[r_num] if r_num < len(pool) else None
                raw_row[qt] = val
                cleaned_row[qk] = val

            responses.append({
                "response_number": r_num + 1,
                "submission_timestamp": datetime.datetime.utcnow(),
                "raw_data": raw_row,
                "cleaned_data": cleaned_row,
                "is_valid": True
            })

        return responses

    @staticmethod
    def parse_csv_content(csv_content: str, source_title: str = "Imported Form") -> Dict[str, Any]:
        """
        Parses CSV data (from Google Sheets or direct file upload) into normalized questions and responses.
        """
        df = pd.read_csv(io.StringIO(csv_content))
        if df.empty or len(df.columns) == 0:
            raise ValueError("The uploaded or linked dataset contains no rows or columns.")

        # Clean and strip all column headers to prevent key mismatches
        df.columns = [str(c).strip() for c in df.columns]

        # Identify timestamp column if exists
        timestamp_col = None
        for col in df.columns:
            if "timestamp" in col.lower() or "time" in col.lower() or "date" in col.lower():
                timestamp_col = col
                break

        questions = []
        q_idx = 1
        for col in df.columns:
            if col == timestamp_col:
                continue
                
            q_key = f"Q{q_idx}"
            col_series = df[col].dropna()
            
            # Infer question type and data type
            inferred_type = "text"
            q_type = "short_answer"
            scale_min = None
            scale_max = None
            options = []

            # Check if numeric
            is_numeric = False
            try:
                numeric_series = pd.to_numeric(col_series, errors='coerce').dropna()
                if len(numeric_series) > 0 and len(numeric_series) / max(1, len(col_series)) > 0.8:
                    is_numeric = True
                    scale_min = int(numeric_series.min())
                    scale_max = int(numeric_series.max())
                    if scale_max <= 10 and scale_min >= 0 and scale_max > scale_min:
                        q_type = "rating" if scale_max == 5 or scale_max == 10 else "linear_scale"
                        inferred_type = "numeric"
                    else:
                        inferred_type = "numeric"
                        q_type = "linear_scale"
            except Exception:
                pass

            if not is_numeric:
                unique_vals = col_series.astype(str).unique().tolist()
                # Check for multiselect checkbox (contains commas or semicolons)
                sample_commas = [v for v in unique_vals if "," in v or ";" in v]
                if len(sample_commas) > 0:
                    q_type = "checkboxes"
                    inferred_type = "multiselect"
                    # Extract unique options
                    opt_set = set()
                    for v in unique_vals:
                        parts = [p.strip() for p in re.split(r'[,;]\s*', v) if p.strip()]
                        opt_set.update(parts)
                    options = sorted(list(opt_set))[:20]
                elif len(unique_vals) <= 10 and len(unique_vals) > 0:
                    if set(v.lower() for v in unique_vals).issubset({"yes", "no", "maybe"}):
                        q_type = "yes_no"
                        inferred_type = "categorical"
                        options = unique_vals
                    else:
                        q_type = "multiple_choice"
                        inferred_type = "categorical"
                        options = unique_vals
                else:
                    # Longer text or open-ended
                    avg_len = col_series.astype(str).str.len().mean() if len(col_series) > 0 else 0
                    if avg_len > 40:
                        q_type = "paragraph"
                        inferred_type = "text"
                    else:
                        q_type = "short_answer"
                        inferred_type = "text"

            questions.append({
                "question_key": q_key,
                "question_text": str(col).strip(),
                "question_type": q_type,
                "inferred_data_type": inferred_type,
                "options": options,
                "scale_min": scale_min,
                "scale_max": scale_max,
                "is_required": False
            })
            q_idx += 1

        # Extract rows
        responses = []
        for idx, row in df.iterrows():
            raw_row = {}
            cleaned_row = {}
            ts_val = None
            if timestamp_col and pd.notna(row.get(timestamp_col)):
                raw_ts = str(row.get(timestamp_col))
                raw_row["Timestamp"] = raw_ts
                try:
                    ts_parsed = pd.to_datetime(raw_ts)
                    if pd.isna(ts_parsed) or ts_parsed is pd.NaT:
                        ts_val = None
                    elif hasattr(ts_parsed, "to_pydatetime"):
                        ts_val = ts_parsed.to_pydatetime()
                        if pd.isna(ts_val):
                            ts_val = None
                    else:
                        ts_val = ts_parsed
                except Exception:
                    ts_val = None

            for q in questions:
                raw_v = row.get(q["question_text"])
                if pd.isna(raw_v):
                    raw_row[q["question_text"]] = None
                    cleaned_row[q["question_key"]] = None
                else:
                    raw_row[q["question_text"]] = raw_v
                    # Cleaned representation
                    if q["inferred_data_type"] == "numeric":
                        try:
                            cleaned_row[q["question_key"]] = float(raw_v)
                        except Exception:
                            cleaned_row[q["question_key"]] = None
                    elif q["inferred_data_type"] == "multiselect":
                        parts = [p.strip() for p in re.split(r'[,;]\s*', str(raw_v)) if p.strip()]
                        cleaned_row[q["question_key"]] = parts
                    else:
                        cleaned_row[q["question_key"]] = str(raw_v).strip()

            responses.append({
                "response_number": idx + 1,
                "submission_timestamp": ts_val,
                "raw_data": raw_row,
                "cleaned_data": cleaned_row,
                "is_valid": True
            })

        return {
            "title": source_title,
            "description": f"Dataset imported with {len(questions)} questions and {len(responses)} responses.",
            "source_type": "csv_import",
            "questions": questions,
            "responses": responses
        }
