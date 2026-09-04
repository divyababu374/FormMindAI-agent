from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, Optional
import datetime

class ReportGenerateRequest(BaseModel):
    report_type: str = "full"  # full, executive_summary, one_page, five_page, negative_feedback, leadership, custom
    custom_instructions: Optional[str] = None
    title: Optional[str] = None

class ReportResponse(BaseModel):
    id: str
    form_id: str
    report_type: str
    title: str
    content_markdown: str
    structure_json: Dict[str, Any] = {}
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class FileExportResponse(BaseModel):
    id: str
    form_id: str
    file_type: str
    file_name: str
    file_size_bytes: int
    download_url: str
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class InfographicGenerateRequest(BaseModel):
    theme: str = "modern_blue" # modern_blue, dark_slate, emerald, sunset
    include_charts: bool = True
    aspect_ratio: str = "portrait" # portrait, landscape, square
