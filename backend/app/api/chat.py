import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.user import User
from app.models.form import Form
from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatSessionResponse
from app.utils.security import get_current_user
from app.services.chat.grounded_chat import GroundedChatEngine

router = APIRouter(prefix="/forms/{form_id}/chat", tags=["AI Chat"])

@router.post("", response_model=ChatMessageResponse)
def send_chat_message(
    form_id: str,
    msg_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = db.query(Form).filter(Form.id == form_id, or_(Form.user_id == current_user.id, Form.user_id == "demo_user_default", Form.connected_email == current_user.email)).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

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

    # Retrieve past messages
    history_records = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    chat_history = [{"role": m.role, "content": m.content} for m in history_records[-10:]]

    # Run Grounded Chat
    ai_result = GroundedChatEngine.process_query(
        user_message=msg_in.content,
        form=form,
        questions=questions,
        responses=responses,
        analysis_data=analysis_data,
        chat_history=chat_history
    )

    # Save Assistant Response
    assistant_msg = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        role="assistant",
        content=ai_result.get("content", "Analysis calculated."),
        chart_data=ai_result.get("chart_data"),
        grounded_facts=ai_result.get("grounded_facts"),
        intent_detected=ai_result.get("intent_detected"),
        file_attachment=ai_result.get("file_attachment")
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg

@router.get("/history", response_model=ChatSessionResponse)
def get_chat_history(
    form_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    form = db.query(Form).filter(Form.id == form_id, or_(Form.user_id == current_user.id, Form.user_id == "demo_user_default", Form.connected_email == current_user.email)).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

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
    form = db.query(Form).filter(Form.id == form_id, or_(Form.user_id == current_user.id, Form.user_id == "demo_user_default", Form.connected_email == current_user.email)).first()
    if not form:
        raise HTTPException(status_code=404, detail="Form not found.")

    session = db.query(ChatSession).filter(ChatSession.form_id == form_id).first()
    if session:
        db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
        db.commit()

    return {"status": "success", "message": "Chat history cleared."}
