import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form as FastForm, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.form import Form
from app.models.account import ConnectedAccount, ConnectedDriveForm
from app.models.question import FormQuestion
from app.models.response import FormResponse, ResponseAnswer
from app.models.analysis import FormAnalysis
from app.models.chat import ChatSession
from app.models.attachment import Attachment
from app.schemas.form import (
    FormAnalyzeRequest, FormAttachResponsesRequest, FormSummaryResponse, FormDetailResponse,
    FormQuestionResponse, FormResponseItem, AnalysisResultResponse, PaginatedResponses,
    FormDataStatusResponse
)
from app.utils.security import get_current_user
from app.services.ingestion.url_parser import parse_and_validate_url
from app.services.ingestion.google_connector import GoogleConnector
from app.services.ingestion.microsoft_connector import MicrosoftConnector
from app.services.ingestion.demo_datasets import get_workshop_feedback_dataset, get_customer_satisfaction_dataset
from app.services.ingestion.file_importer import import_file_to_dataset
from app.services.cleaning.data_cleaner import DataCleaner
from app.services.analytics.stats_engine import StatsEngine
from app.services.analytics.text_analyzer import TextAnalyzer
from app.services.analytics.comparative_engine import ComparativeEngine
from app.services.ai.ai_factory import get_ai_provider
from app.api.auth import get_valid_google_token

router = APIRouter(prefix="/forms", tags=["Forms & Analysis"])

def _process_and_save_dataset(dataset: dict, user: User, db: Session, source_url: Optional[str] = None) -> Form:
    # 1. Clean dataset
    raw_questions = dataset.get("questions", [])
    raw_responses = dataset.get("responses", [])
    raw_attachments = dataset.get("attachments", [])
    access_status = dataset.get("response_access_status") or ("ready" if raw_responses else "zero_responses")
    
    cleaned_questions, cleaned_responses, cleaning_summary = DataCleaner.clean_dataset(raw_questions, raw_responses)
    has_responses = len(cleaned_responses) > 0

    # 2. Run statistical computations only if actual responses exist
    if has_responses:
        stats = StatsEngine.calculate_all(cleaned_questions, cleaned_responses)
        text_analysis = TextAnalyzer.analyze_text_responses(cleaned_questions, cleaned_responses)
        comparisons = ComparativeEngine.compare_segments(cleaned_questions, cleaned_responses)
        ai_provider = get_ai_provider()
        form_title = dataset.get("title", "Survey Form")
        form_desc = dataset.get("description", "")
        insights = ai_provider.generate_form_insights(form_title, form_desc, stats, text_analysis, comparisons)
        analysis_status = "ready"
        completion_rate = stats.get("basic", {}).get("completion_rate", "100%")
        ai_provider_name = getattr(ai_provider, "__class__", {}).__name__
    else:
        stats = {
            "basic": {
                "total_responses": 0,
                "total_questions": len(cleaned_questions),
                "completion_rate": "0%",
                "avg_responses_per_question": 0,
                "submission_trend": []
            },
            "numerical": {},
            "categorical": {}
        }
        text_analysis = {
            "overall_sentiment": {"positive_pct": 0, "neutral_pct": 0, "negative_pct": 0, "compound_score": 0},
            "sentiment_classification": "No responses yet",
            "top_keywords": [],
            "key_themes": [],
            "analyzed_questions": {}
        }
        comparisons = []
        insights = {
            "executive_summary": "This form currently has 0 responses. Submit responses or sync from Google to generate analysis.",
            "key_insights": [],
            "actionable_recommendations": [],
            "sentiment_summary": "No submitted responses to analyze."
        }
        analysis_status = "unavailable"
        completion_rate = "0%"
        ai_provider_name = "DeterministicEngine"

    try:
        # Determine connected email for this user
        conn_email = None
        if user and user.email and "@" in user.email and not user.email.endswith("@demo.formmind.ai"):
            conn_email = user.email.strip().lower()
        elif user:
            acc = db.query(ConnectedAccount).filter(
                ConnectedAccount.user_id == user.id,
                ConnectedAccount.is_active == True
            ).first()
            if acc and acc.email:
                conn_email = acc.email.strip().lower()

        # 3. Save Form Record
        form_id = str(uuid.uuid4())
        form = Form(
            id=form_id,
            user_id=user.id,
            connected_email=conn_email,
            title=dataset.get("title", "Survey Form"),
            description=dataset.get("description", ""),
            source_url=source_url or dataset.get("source_url"),
            source_type=dataset.get("source_type", "google_form"),
            total_responses_count=len(cleaned_responses),
            questions_count=len(cleaned_questions),
            completion_rate=completion_rate,
            status="completed",
            status_message=dataset.get("status_message") or ("No responses yet." if not has_responses else None),
            form_metadata_status="ready" if cleaned_questions else "failed",
            response_access_status=access_status,
            response_sync_status="synced" if has_responses else "pending",
            analysis_status=analysis_status,
            attachment_status="ready" if raw_attachments else "none",
            last_synced_at=datetime.datetime.utcnow(),
            meta_info={"cleaning_summary": cleaning_summary}
        )
        db.add(form)

        # 4. Save Questions
        question_map = {}
        for idx, q_data in enumerate(cleaned_questions):
            q_id = str(uuid.uuid4())
            q_key = q_data["question_key"]
            question = FormQuestion(
                id=q_id,
                form_id=form_id,
                question_key=q_key,
                question_index=idx,
                question_text=q_data["question_text"],
                question_type=q_data.get("question_type", "multiple_choice"),
                options=q_data.get("options", []),
                is_required=q_data.get("is_required", False),
                inferred_data_type=q_data.get("inferred_data_type", "text"),
                scale_min=q_data.get("scale_min"),
                scale_max=q_data.get("scale_max")
            )
            db.add(question)
            question_map[q_key] = question

        # 5. Save Responses & Answers
        for r_data in cleaned_responses:
            resp_id = str(uuid.uuid4())
            resp = FormResponse(
                id=resp_id,
                form_id=form_id,
                google_response_id=r_data.get("google_response_id"),
                response_number=r_data.get("response_number", 1),
                submission_timestamp=r_data.get("submission_timestamp"),
                raw_data=r_data.get("raw_data", {}),
                cleaned_data=r_data.get("cleaned_data", {}),
                is_valid=True
            )
            db.add(resp)

            for q_key, q_obj in question_map.items():
                raw_val = r_data.get("raw_data", {}).get(q_obj.question_text)
                if raw_val is None:
                    for k, v in r_data.get("raw_data", {}).items():
                        if k.strip().lower() == q_obj.question_text.strip().lower():
                            raw_val = v
                            break
                clean_val = r_data.get("cleaned_data", {}).get(q_key)
                if clean_val is None and raw_val is not None:
                    clean_val = raw_val

                ans = ResponseAnswer(
                    id=str(uuid.uuid4()),
                    response_id=resp_id,
                    question_id=q_obj.id,
                    raw_value=str(raw_val) if raw_val is not None else None,
                    cleaned_value=str(clean_val) if clean_val is not None else None,
                    parsed_json_value=clean_val if isinstance(clean_val, (list, dict)) else None
                )
                db.add(ans)


        # 6. Save Attachments
        for att in raw_attachments:
            att_obj = Attachment(
                id=str(uuid.uuid4()),
                form_id=form_id,
                file_name=att.get("file_name", "Attachment"),
                mime_type=att.get("mime_type"),
                drive_file_id=att.get("drive_file_id"),
                processing_status="analyzed" if att.get("file_name") else "unsupported",
                meta_info=att
            )
            db.add(att_obj)

        # 7. Save Analysis
        analysis_id = str(uuid.uuid4())
        form_analysis = FormAnalysis(
            id=analysis_id,
            form_id=form_id,
            executive_summary=insights.get("executive_summary"),
            basic_statistics=stats.get("basic", {}),
            numerical_analysis=stats.get("numerical", {}),
            categorical_analysis=stats.get("categorical", {}),
            text_analysis=text_analysis,
            comparative_analysis=comparisons,
            ai_insights=insights,
            ai_provider_used=ai_provider_name
        )
        db.add(form_analysis)

        # 8. Create default chat session
        chat_session = ChatSession(
            id=str(uuid.uuid4()),
            form_id=form_id,
            title=f"Chat: {form.title}"
        )
        db.add(chat_session)

        db.commit()
        db.refresh(form)
        return form
    except Exception as exc:
        db.rollback()
        raise exc

@router.post("/analyze", response_model=FormSummaryResponse)
def analyze_form(req: FormAnalyzeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Ingests and analyzes a Google Form URL, Microsoft Forms URL, Google Sheet URL, or Demo Dataset.
    """
    # Demo dataset option
    if req.demo_type:
        if req.demo_type in ("ms_employee_feedback", "microsoft_form_demo", "ms_form"):
            dataset = MicrosoftConnector.get_microsoft_forms_demo_dataset()
        elif req.demo_type == "customer_nps":
            dataset = get_customer_satisfaction_dataset()
        else:
            dataset = get_workshop_feedback_dataset()
        if req.title:
            dataset["title"] = req.title
        form = _process_and_save_dataset(dataset, current_user, db)
        return form

    # URL Ingestion
    if not req.url:
        raise HTTPException(status_code=400, detail="Please enter a valid Google Forms or Microsoft Forms URL.")

    parsed = parse_and_validate_url(req.url)
    if not parsed["is_valid"]:
        raise HTTPException(status_code=400, detail=parsed["error_message"])

    try:
        if parsed["source_type"] == "microsoft_form":
            dataset = MicrosoftConnector.fetch_from_form_url(
                req.url,
                linked_sheet_url=req.linked_sheet_url
            )
        else:
            valid_token = get_valid_google_token(current_user, db) if current_user.is_google_connected else current_user.google_access_token
            dataset = GoogleConnector.fetch_from_form_url(
                req.url, 
                access_token=valid_token,
                linked_sheet_url=req.linked_sheet_url
            )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to access form data: {str(e)}")

    if req.title:
        dataset["title"] = req.title

    # Only save actual responses from Google Form / Microsoft Form / Sheet.
    form = _process_and_save_dataset(dataset, current_user, db, source_url=req.url)
    return form


@router.post("/upload", response_model=FormSummaryResponse)
async def upload_form_file(
    file: UploadFile = File(...),
    title: Optional[str] = FastForm(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload CSV or Excel file containing form responses.
    """
    try:
        contents = await file.read()
        dataset = import_file_to_dataset(contents, file.filename)
        if title:
            dataset["title"] = title
        form = _process_and_save_dataset(dataset, current_user, db, source_url=file.filename)
        return form
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded dataset: {str(e)}")

def _get_form_for_user(form_id: str, current_user: User, db: Session) -> Optional[Form]:
    if current_user and current_user.id != "demo_user_default":
        connected_emails = []
        if current_user.email:
            connected_emails.append(current_user.email.strip().lower())
        conn_accs = db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.is_active == True
        ).all()
        for acc in conn_accs:
            if acc.email and acc.email.strip().lower() not in connected_emails:
                connected_emails.append(acc.email.strip().lower())

        conditions = [Form.user_id == current_user.id]
        if connected_emails:
            conditions.append(Form.connected_email.in_(connected_emails))

        return db.query(Form).filter(
            Form.id == form_id,
            or_(*conditions)
        ).first()
    else:
        return db.query(Form).filter(
            Form.id == form_id,
            Form.user_id == "demo_user_default"
        ).first()

@router.get("", response_model=List[FormSummaryResponse])
def get_user_forms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lists all forms belonging to the current user or their connected email.
    """
    if current_user and current_user.id != "demo_user_default":
        connected_emails = []
        if current_user.email:
            connected_emails.append(current_user.email.strip().lower())
        conn_accs = db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.is_active == True
        ).all()
        for acc in conn_accs:
            if acc.email and acc.email.strip().lower() not in connected_emails:
                connected_emails.append(acc.email.strip().lower())

        conditions = [Form.user_id == current_user.id]
        if connected_emails:
            conditions.append(Form.connected_email.in_(connected_emails))

        forms = db.query(Form).filter(or_(*conditions)).order_by(Form.created_at.desc()).all()
        return forms
    else:
        forms = db.query(Form).filter(Form.user_id == "demo_user_default").order_by(Form.created_at.desc()).all()
        return forms

@router.get("/google/drive-forms")
def get_user_google_forms(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lists Google Forms from the connected user's Google Drive and persists them to the database.
    """
    token = get_valid_google_token(current_user, db) if current_user.is_google_connected else current_user.google_access_token
    if not token:
        conn_acc = db.query(ConnectedAccount).filter(
            ConnectedAccount.user_id == current_user.id,
            ConnectedAccount.provider == "google",
            ConnectedAccount.is_active == True
        ).first()
        if conn_acc and conn_acc.access_token:
            token = conn_acc.access_token

    drive_forms = []
    if token:
        try:
            drive_forms = GoogleConnector.list_user_drive_forms(token)
            conn_email = current_user.email
            for df in drive_forms:
                existing_cdf = db.query(ConnectedDriveForm).filter(
                    ConnectedDriveForm.user_id == current_user.id,
                    ConnectedDriveForm.google_form_id == df["id"]
                ).first()
                if existing_cdf:
                    existing_cdf.title = df.get("name", existing_cdf.title)
                    existing_cdf.edit_url = df.get("edit_url", existing_cdf.edit_url)
                    existing_cdf.view_url = df.get("view_url", existing_cdf.view_url)
                    existing_cdf.modified_time = df.get("modified_time", existing_cdf.modified_time)
                else:
                    new_cdf = ConnectedDriveForm(
                        id=str(uuid.uuid4()),
                        user_id=current_user.id,
                        connected_email=conn_email,
                        google_form_id=df["id"],
                        title=df.get("name", "Google Form"),
                        edit_url=df.get("edit_url"),
                        view_url=df.get("view_url"),
                        created_time=df.get("created_time"),
                        modified_time=df.get("modified_time")
                    )
                    db.add(new_cdf)
            db.commit()
        except Exception:
            pass

    if not drive_forms:
        saved_drive_forms = db.query(ConnectedDriveForm).filter(
            or_(
                ConnectedDriveForm.user_id == current_user.id,
                ConnectedDriveForm.connected_email == current_user.email
            )
        ).all()
        drive_forms = [
            {
                "id": sdf.google_form_id,
                "name": sdf.title,
                "edit_url": sdf.edit_url,
                "view_url": sdf.view_url,
                "created_time": sdf.created_time,
                "modified_time": sdf.modified_time
            }
            for sdf in saved_drive_forms
        ]

    return drive_forms

@router.get("/{form_id}", response_model=FormDetailResponse)
def get_form_detail(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Retrieves full form details with question schema.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return form

@router.delete("/{form_id}")
def delete_form(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Deletes a form and cascades to all responses, analysis, chat sessions, and generated files.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    db.delete(form)
    db.commit()
    return {"status": "success", "message": "Form and all associated data permanently deleted."}

@router.get("/{form_id}/questions", response_model=List[FormQuestionResponse])
def get_form_questions(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return form.questions

@router.get("/{form_id}/analysis", response_model=AnalysisResultResponse)
def get_form_analysis(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    form = _get_form_for_user(form_id, current_user, db)
    if not form or not form.analysis:
        raise HTTPException(status_code=404, detail="Analysis not found for this form.")
    return form.analysis

@router.get("/{form_id}/responses", response_model=PaginatedResponses)
def get_form_responses(
    form_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=5, le=100),
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    query = db.query(FormResponse).filter(FormResponse.form_id == form_id)

    # Search filter
    all_responses = query.all()
    filtered = []
    for r in all_responses:
        if search:
            s_lower = search.lower()
            row_str = str(r.cleaned_data).lower() + " " + str(r.raw_data).lower()
            if s_lower not in row_str:
                continue
        filtered.append(r)

    # Sort
    if sort_by:
        filtered.sort(
            key=lambda x: str(x.cleaned_data.get(sort_by, "")) if x.cleaned_data else "",
            reverse=sort_desc
        )
    else:
        filtered.sort(key=lambda x: x.response_number, reverse=sort_desc)

    total = len(filtered)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = filtered[start_idx:end_idx]

    columns = [
        {"key": "response_number", "label": "#", "type": "number"},
        {"key": "submission_timestamp", "label": "Timestamp", "type": "datetime"}
    ]
    for q in form.questions:
        columns.append({
            "key": q.question_key,
            "label": q.question_text,
            "type": q.inferred_data_type
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
        "items": items,
        "columns": columns
    }

@router.get("/{form_id}/data-status", response_model=FormDataStatusResponse)
def get_form_data_status(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns actual counts and status across Google API, local DB, attachments, and sync status.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    db_responses_count = db.query(FormResponse).filter(FormResponse.form_id == form_id).count()
    att_count = db.query(Attachment).filter(Attachment.form_id == form_id).count()

    return FormDataStatusResponse(
        form_id=form.id,
        form_title=form.title,
        questions_count=form.questions_count,
        google_response_count=form.total_responses_count,
        database_response_count=db_responses_count,
        form_metadata_status=form.form_metadata_status or "ready",
        response_access_status=form.response_access_status or "ready",
        response_sync_status=form.response_sync_status or "synced",
        analysis_status=form.analysis_status or "ready",
        attachment_status=form.attachment_status or "none",
        attachments_count=att_count,
        last_synced_at=form.last_synced_at
    )

def _insert_responses_and_recompute(form: Form, raw_responses: list, db: Session, access_status: str = "ready") -> Form:
    if not raw_responses:
        return form

    # 1. Build question mappings
    question_map = {q.question_key: q for q in form.questions}
    
    q_dict_list = []

    for q in form.questions:
        opts = q.options
        if isinstance(opts, str):
            try:
                import json
                opts = json.loads(opts)
            except Exception:
                opts = []
        elif not opts:
            opts = []
        q_dict_list.append({
            "question_key": q.question_key,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "inferred_data_type": q.inferred_data_type,
            "options": opts,
            "scale_min": q.scale_min,
            "scale_max": q.scale_max,
            "is_required": q.is_required
        })
    
    cleaned_q, cleaned_resp, _ = DataCleaner.clean_dataset(q_dict_list, raw_responses)
    
    current_max_number = db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
    existing_google_ids = set()
    for r in db.query(FormResponse.google_response_id).filter(FormResponse.form_id == form.id).all():
        if r[0]:
            existing_google_ids.add(r[0])

    for r_data in cleaned_resp:
        g_id = r_data.get("google_response_id")
        if g_id and g_id in existing_google_ids:
            continue

        current_max_number += 1
        resp_id = str(uuid.uuid4())
        resp = FormResponse(
            id=resp_id,
            form_id=form.id,
            google_response_id=g_id,
            response_number=current_max_number,
            submission_timestamp=r_data.get("submission_timestamp") or datetime.datetime.utcnow(),
            raw_data=r_data.get("raw_data", {}),
            cleaned_data=r_data.get("cleaned_data", {}),
            is_valid=True
        )
        db.add(resp)

        for q_key, q_obj in question_map.items():
            raw_val = r_data.get("raw_data", {}).get(q_obj.question_text)
            if raw_val is None:
                for k, v in r_data.get("raw_data", {}).items():
                    if k.strip().lower() == q_obj.question_text.strip().lower():
                        raw_val = v
                        break
            clean_val = r_data.get("cleaned_data", {}).get(q_key)
            if clean_val is None and raw_val is not None:
                clean_val = raw_val

            ans = ResponseAnswer(
                id=str(uuid.uuid4()),
                response_id=resp_id,
                question_id=q_obj.id,
                raw_value=str(raw_val) if raw_val is not None else None,
                cleaned_value=str(clean_val) if clean_val is not None else None,
                parsed_json_value=clean_val if isinstance(clean_val, (list, dict)) else None
            )
            db.add(ans)

        if g_id:
            existing_google_ids.add(g_id)

    db.flush()

    # Recalculate analysis over all stored responses
    all_stored_responses = db.query(FormResponse).filter(FormResponse.form_id == form.id).all()
    normalized_resp_list = [
        {
            "response_number": r.response_number,
            "submission_timestamp": r.submission_timestamp,
            "raw_data": r.raw_data,
            "cleaned_data": r.cleaned_data,
            "is_valid": r.is_valid
        }
        for r in all_stored_responses
    ]

    if len(normalized_resp_list) > 0:
        stats = StatsEngine.calculate_all(q_dict_list, normalized_resp_list)
        text_analysis = TextAnalyzer.analyze_text_responses(q_dict_list, normalized_resp_list)
        comparisons = ComparativeEngine.compare_segments(q_dict_list, normalized_resp_list)
        ai_provider = get_ai_provider()
        insights = ai_provider.generate_form_insights(form.title, form.description or "", stats, text_analysis, comparisons)

        if form.analysis:
            form.analysis.basic_statistics = stats.get("basic", {})
            form.analysis.numerical_analysis = stats.get("numerical", {})
            form.analysis.categorical_analysis = stats.get("categorical", {})
            form.analysis.text_analysis = text_analysis
            form.analysis.comparative_analysis = comparisons
            form.analysis.ai_insights = insights
            form.analysis.executive_summary = insights.get("executive_summary")
        else:
            analysis_id = str(uuid.uuid4())
            form.analysis = FormAnalysis(
                id=analysis_id,
                form_id=form.id,
                executive_summary=insights.get("executive_summary"),
                basic_statistics=stats.get("basic", {}),
                numerical_analysis=stats.get("numerical", {}),
                categorical_analysis=stats.get("categorical", {}),
                text_analysis=text_analysis,
                comparative_analysis=comparisons,
                ai_insights=insights,
                ai_provider_used=getattr(ai_provider, "__class__", {}).__name__
            )
            db.add(form.analysis)

        form.analysis_status = "ready"
        form.completion_rate = stats.get("basic", {}).get("completion_rate", "100%")
        form.response_access_status = access_status or "ready"
        form.status_message = None
    else:
        form.analysis_status = "unavailable"
        form.completion_rate = "0%"

    form.total_responses_count = len(normalized_resp_list)
    form.response_sync_status = "synced"
    form.last_synced_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(form)
    return form

@router.post("/{form_id}/sync", response_model=FormDataStatusResponse)
def sync_latest_responses(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Synchronizes latest responses from Google Form API or linked Google Sheet.
    Prevents duplicates, processes new responses, and updates analytics.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    if not form.source_url:
        raise HTTPException(status_code=400, detail="Cannot sync form without source URL.")

    form.response_sync_status = "syncing"
    db.commit()

    try:
        if form.source_type == "microsoft_form":
            dataset = MicrosoftConnector.fetch_from_form_url(form.source_url)
        else:
            valid_token = get_valid_google_token(current_user, db) if current_user.is_google_connected else current_user.google_access_token
            dataset = GoogleConnector.fetch_from_form_url(form.source_url, access_token=valid_token)
        new_responses = dataset.get("responses", [])
        
        if new_responses:
            _insert_responses_and_recompute(form, new_responses, db, access_status="ready")
        else:
            form.response_sync_status = "synced"
            form.last_synced_at = datetime.datetime.utcnow()
            if dataset.get("response_access_status"):
                form.response_access_status = dataset["response_access_status"]
            if dataset.get("status_message"):
                form.status_message = dataset["status_message"]
            db.commit()
            db.refresh(form)


        stored_count = db.query(FormResponse).filter(FormResponse.form_id == form.id).count()
        return FormDataStatusResponse(
            form_id=form.id,
            form_title=form.title,
            questions_count=form.questions_count,
            google_response_count=form.total_responses_count,
            database_response_count=stored_count,
            form_metadata_status=form.form_metadata_status or "ready",
            response_access_status=form.response_access_status or "ready",
            response_sync_status=form.response_sync_status or "synced",
            analysis_status=form.analysis_status or "ready",
            attachment_status=form.attachment_status or "none",
            attachments_count=db.query(Attachment).filter(Attachment.form_id == form.id).count(),
            last_synced_at=form.last_synced_at
        )
    except Exception as e:
        form.response_sync_status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Response synchronization failed: {str(e)}")

@router.post("/{form_id}/attach-sheet", response_model=FormSummaryResponse)
def attach_responses_sheet(
    form_id: str, 
    req: FormAttachResponsesRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Attaches a Google Sheet containing submitted responses to an existing Google Form.
    Fetches the responses, maps questions, updates database, and recalculates analytics.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    if not req.sheet_url:
        raise HTTPException(status_code=400, detail="Please provide a valid Google Sheet URL.")

    parsed_sheet = parse_and_validate_url(req.sheet_url)
    if not parsed_sheet["is_valid"]:
        raise HTTPException(status_code=400, detail=parsed_sheet.get("error_message") or "Invalid URL provided.")

    if parsed_sheet["source_type"] == "google_form":
        raise HTTPException(
            status_code=400, 
            detail="The URL provided is a Google Form URL. To attach responses, please open your Google Form, click the 'Responses' tab, click 'Link to Sheets' (green Sheets icon), and paste that Google Spreadsheet URL here, or upload your exported CSV file."
        )

    if parsed_sheet["source_type"] != "google_sheet":
        raise HTTPException(status_code=400, detail="The provided link is not a valid Google Sheet URL. Please paste a Google Spreadsheet link.")

    try:
        valid_token = get_valid_google_token(current_user, db) if current_user.is_google_connected else current_user.google_access_token
        sheet_dataset = GoogleConnector.fetch_from_sheet_url(
            parsed_sheet["resource_id"], 
            valid_token, 
            is_published_web=parsed_sheet.get("is_published_web", False)
        )
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to access Google Sheet: {str(e)}")

    new_responses = sheet_dataset.get("responses", [])
    if not new_responses:
        raise HTTPException(status_code=400, detail="No response rows found in the provided spreadsheet. Please ensure the sheet has response data.")

    _insert_responses_and_recompute(form, new_responses, db, access_status="ready")
    return form


@router.post("/{form_id}/upload-responses", response_model=FormSummaryResponse)
async def upload_form_responses(
    form_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads a CSV or Excel responses export file into an existing form to populate responses and analytics.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    filename = file.filename or "responses.csv"
    if not filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV, XLSX, and XLS response files are supported.")

    try:
        content = await file.read()
        dataset = import_file_to_dataset(content, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse response file: {str(e)}")

    new_responses = dataset.get("responses", [])
    if not new_responses:
        raise HTTPException(status_code=400, detail="The uploaded file contains no data rows.")

    _insert_responses_and_recompute(form, new_responses, db, access_status="ready")
    return form

@router.get("/{form_id}/attachments")
def get_form_attachments(form_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Lists attachments and their processing statuses.
    """
    form = _get_form_for_user(form_id, current_user, db)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    attachments = db.query(Attachment).filter(Attachment.form_id == form_id).all()
    return [
        {
            "id": a.id,
            "file_name": a.file_name,
            "mime_type": a.mime_type,
            "drive_file_id": a.drive_file_id,
            "processing_status": a.processing_status,
            "summary": a.summary,
            "created_at": a.created_at
        }
        for a in attachments
    ]
