from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
import datetime

class FormAnalyzeRequest(BaseModel):
    url: Optional[str] = None
    linked_sheet_url: Optional[str] = None  # Optional Google Sheet URL with submitted responses
    demo_type: Optional[str] = None  # e.g., 'workshop_feedback', 'customer_nps', 'employee_pulse'
    title: Optional[str] = None

class FormAttachResponsesRequest(BaseModel):
    sheet_url: Optional[str] = None

class FormQuestionResponse(BaseModel):
    id: str
    question_key: str
    question_index: int
    question_text: str
    question_type: str
    options: List[str] = []
    is_required: bool
    inferred_data_type: str
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class FormResponseItem(BaseModel):
    id: str
    response_number: int
    submission_timestamp: Optional[datetime.datetime] = None
    raw_data: Dict[str, Any] = {}
    cleaned_data: Dict[str, Any] = {}
    is_valid: bool

    model_config = ConfigDict(from_attributes=True)

class FormSummaryResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    source_type: str
    total_responses_count: int
    questions_count: int
    completion_rate: str
    status: str
    status_message: Optional[str] = None
    form_metadata_status: Optional[str] = "ready"
    response_access_status: Optional[str] = "ready"
    response_sync_status: Optional[str] = "synced"
    analysis_status: Optional[str] = "ready"
    attachment_status: Optional[str] = "none"
    last_synced_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class FormDataStatusResponse(BaseModel):
    form_id: str
    form_title: str
    questions_count: int
    google_response_count: int
    database_response_count: int
    form_metadata_status: str
    response_access_status: str
    response_sync_status: str
    analysis_status: str
    attachment_status: str
    attachments_count: int
    last_synced_at: Optional[datetime.datetime] = None

class FormDetailResponse(FormSummaryResponse):
    questions: List[FormQuestionResponse] = []
    meta_info: Dict[str, Any] = {}

class AnalysisResultResponse(BaseModel):
    id: str
    form_id: str
    executive_summary: Optional[str] = None
    basic_statistics: Dict[str, Any] = {}
    numerical_analysis: Dict[str, Any] = {}
    categorical_analysis: Dict[str, Any] = {}
    text_analysis: Dict[str, Any] = {}
    comparative_analysis: List[Dict[str, Any]] = []
    ai_insights: Dict[str, Any] = {}
    ai_provider_used: str
    model_name_used: Optional[str] = None
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedResponses(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[FormResponseItem]
    columns: List[Dict[str, Any]]
