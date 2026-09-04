from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional
import datetime

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    chart_data: Optional[Dict[str, Any]] = None
    grounded_facts: Optional[Dict[str, Any]] = None
    file_attachment: Optional[Dict[str, Any]] = None
    intent_detected: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class ChatSessionResponse(BaseModel):
    id: str
    form_id: str
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    messages: List[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
