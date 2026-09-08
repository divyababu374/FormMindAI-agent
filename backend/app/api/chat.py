import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.form import Form
from app.models.chat import ChatSession, ChatMessage
from app.models.analysis import FormAnalysis
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatSessionResponse
from app.utils.security import get_current_user
from app.services.chat.grounded_chat import GroundedChatEngine

router = APIRouter(prefix="/forms/{form_id}/chat", tags=["AI Chat"])

def _get_form_for_chat(form_id: str, current_user: User, db: Session) -> Form:
    if current_user.id != "demo_user_default":
        conds = [Form.user_id == current_user.id]
        if current_user.email:
            conds.append(Form.connected_email == current_user.email)
        form = db.query(Form).filter(Form.id == form_id, or_(*conds)).first()
    else:
        form = db.query(Form).filter(Form.id == form_id, Form.user_id == "demo_user_default").first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")
    return form

@router.post("", response_model=ChatMessageResponse)
def send_chat_message(
    form_id: str,
    msg_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = _get_form_for_chat(form_id, current_user, db)

    # Retrieve or create session
    session = db.query(ChatSession).filter(ChatSession.form_id == form_id).first()
    if not session:
        session = ChatSession(id=str(uuid.uuid4()), form_id=form_id, title=f"Chat: {form.title}")
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="user",
        content=msg_in.content
    )
    db.add(user_msg)
    db.commit()

    # Load questions, responses, analysis
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
            "cleaned_data": r.cleaned_data or {},
            "raw_data": r.raw_data or {}
        }
        for r in form.responses
    ]

    analysis_data = {}
    if form.analysis:
        analysis_data = {
            "basic_statistics": form.analysis.basic_statistics or {},
            "numerical_analysis": form.analysis.numerical_analysis or {},
            "categorical_analysis": form.analysis.categorical_analysis or {},
            "text_analysis": form.analysis.text_analysis or {},
            "comparative_analysis": form.analysis.comparative_analysis or [],
            "ai_insights": form.analysis.ai_insights or {}
        }
    responses = [r.cleaned_data for r in form.responses if r.cleaned_data]
    analysis = db.query(FormAnalysis).filter(FormAnalysis.form_id == form_id).first()
    analysis_dict = {
        "basic_statistics": analysis.basic_statistics if analysis else {},
        "numerical_analysis": analysis.numerical_analysis if analysis else {},
        "categorical_analysis": analysis.categorical_analysis if analysis else {},
        "text_analysis": analysis.text_analysis if analysis else {},
        "comparative_analysis": analysis.comparative_analysis if analysis else [],
        "ai_insights": analysis.ai_insights if analysis else {}
    }

    # Load recent message history
    recent_msgs = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).limit(15).all()

    chat_history = [
        {"role": m.role, "content": m.content}
        for m in recent_msgs
    ]

    # Generate AI answer with grounding
    ai_result = GroundedChatEngine.process_query(
        user_message=msg_in.content,
        form=form,
        questions=questions,
        responses=responses,
        analysis_data=analysis_dict,
        chat_history=chat_history
    )

    # Save assistant message
    asst_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="assistant",
        content=ai_result.get("content", "Analysis calculated."),
        chart_data=ai_result.get("chart_data"),
        grounded_facts=ai_result.get("grounded_facts"),
        intent_detected=ai_result.get("intent_detected"),
        file_attachment=ai_result.get("file_attachment")
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)

    return asst_msg

@router.get("/history", response_model=ChatSessionResponse)
def get_chat_history(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = _get_form_for_chat(form_id, current_user, db)

    session = db.query(ChatSession).filter(ChatSession.form_id == form_id).first()
    if not session:
        session = ChatSession(id=str(uuid.uuid4()), form_id=form_id, title=f"Chat: {form.title}")
        db.add(session)
        db.commit()
        db.refresh(session)

    return session

@router.delete("/history")
def clear_chat_history(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = _get_form_for_chat(form_id, current_user, db)

    session = db.query(ChatSession).filter(ChatSession.form_id == form_id).first()
    if session:
        db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
        db.commit()

    return {"status": "success", "message": "Chat history cleared."}
