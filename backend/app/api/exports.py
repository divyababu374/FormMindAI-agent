import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.form import Form
from app.models.report import GeneratedReport, GeneratedFile
from app.schemas.report import ReportGenerateRequest, ReportResponse, FileExportResponse, InfographicGenerateRequest
from app.utils.security import get_current_user
from app.services.ai.ai_factory import get_ai_provider
from app.services.exports.pdf_generator import generate_pdf_report
from app.services.exports.docx_generator import generate_docx_report
from app.services.exports.xlsx_generator import generate_xlsx_workbook
from app.services.exports.csv_generator import generate_csv_export
from app.services.exports.infographic_generator import generate_infographic_image

router = APIRouter(prefix="/forms/{form_id}", tags=["Reports & File Exports"])

def _get_form_and_data(form_id: str, current_user: User, db: Session):
    form = db.query(Form).filter(Form.id == form_id, Form.user_id == current_user.id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    
    questions = [
        {
            "question_key": q.question_key,
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options or [],
            "inferred_data_type": q.inferred_data_type,
            "scale_min": q.scale_min,
            "scale_max": q.scale_max
        }
        for q in form.questions
    ]

    responses = [
        {
            "response_number": r.response_number,
            "submission_timestamp": r.submission_timestamp,
            "raw_data": r.raw_data or {},
            "cleaned_data": r.cleaned_data or {}
        }
        for r in form.responses
    ]

    num_analysis = form.analysis.numerical_analysis if form.analysis else {}
    avg_rating_str = "N/A"
    if num_analysis:
        means = [v.get("mean") for v in num_analysis.values() if v.get("mean") is not None]
        if means:
            first_num = list(num_analysis.values())[0]
            max_scale = first_num.get("max", 5)
            scale_denom = 10 if max_scale and max_scale > 5 else 5
            avg_rating_str = f"{round(sum(means) / len(means), 1)}/{scale_denom}"

    stats = {
        "basic": form.analysis.basic_statistics if form.analysis else {},
        "numerical": form.analysis.numerical_analysis if form.analysis else {},
        "categorical": form.analysis.categorical_analysis if form.analysis else {},
        "overview_cards": {
            "total_responses": form.total_responses_count,
            "total_questions": form.questions_count,
            "average_rating": avg_rating_str,
            "completion_rate": form.completion_rate
        }
    }
    text_analysis = form.analysis.text_analysis if form.analysis else {}
    comparisons = form.analysis.comparative_analysis if form.analysis else []
    ai_insights = form.analysis.ai_insights if form.analysis else {}

    return form, questions, responses, stats, text_analysis, comparisons, ai_insights

@router.post("/report", response_model=ReportResponse)
def generate_custom_report(
    form_id: str,
    req: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    ai_provider = get_ai_provider()
    report_title = req.title or f"{req.report_type.replace('_', ' ').title()} — {form.title}"
    
    report_md = ai_provider.generate_report_markdown(
        form_title=form.title,
        stats=stats,
        text_analysis=text_analysis,
        comparisons=comparisons,
        report_type=req.report_type,
        custom_instructions=req.custom_instructions
    )

    report = GeneratedReport(
        id=str(uuid.uuid4()),
        form_id=form_id,
        report_type=req.report_type,
        title=report_title,
        content_markdown=report_md,
        structure_json={"scope": req.report_type, "generated_at": str(form.updated_at)}
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

@router.get("/export/pdf")
def export_pdf(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    pdf_path = generate_pdf_report(
        form_id=form.id,
        form_title=form.title,
        form_description=form.description or "",
        stats=stats,
        text_analysis=text_analysis,
        comparisons=comparisons,
        ai_insights=ai_insights
    )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )

@router.get("/export/docx")
def export_docx(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    docx_path = generate_docx_report(
        form_id=form.id,
        form_title=form.title,
        form_description=form.description or "",
        stats=stats,
        text_analysis=text_analysis,
        comparisons=comparisons,
        ai_insights=ai_insights
    )

    return FileResponse(
        path=docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=os.path.basename(docx_path)
    )

@router.get("/export/xlsx")
def export_xlsx(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    xlsx_path = generate_xlsx_workbook(
        form_id=form.id,
        form_title=form.title,
        questions=questions,
        responses=responses,
        stats=stats,
        ai_insights=ai_insights
    )

    return FileResponse(
        path=xlsx_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(xlsx_path)
    )

@router.get("/export/csv")
def export_csv(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    csv_path = generate_csv_export(
        form_id=form.id,
        questions=questions,
        responses=responses
    )

    return FileResponse(
        path=csv_path,
        media_type="text/csv",
        filename=os.path.basename(csv_path)
    )

@router.get("/image")
@router.post("/image")
def export_infographic(
    form_id: str,
    format: str = Query("png", pattern="^(png|jpg|jpeg)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form, questions, responses, stats, text_analysis, comparisons, ai_insights = _get_form_and_data(form_id, current_user, db)
    
    img_path = generate_infographic_image(
        form_id=form.id,
        form_title=form.title,
        stats=stats,
        ai_insights=ai_insights,
        file_format=format
    )

    media_type = "image/jpeg" if format.lower() in ["jpg", "jpeg"] else "image/png"
    return FileResponse(
        path=img_path,
        media_type=media_type,
        filename=os.path.basename(img_path)
    )
