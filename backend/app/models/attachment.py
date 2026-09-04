import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = Column(String(64), ForeignKey("form_responses.id", ondelete="CASCADE"), nullable=True, index=True)
    question_id = Column(String(64), ForeignKey("form_questions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    file_name = Column(String(500), nullable=False)
    mime_type = Column(String(255), nullable=True)
    drive_file_id = Column(String(255), nullable=True, index=True)
    file_size = Column(Integer, nullable=True)
    
    # processing_status: waiting, processing, analyzed, unsupported, failed
    processing_status = Column(String(50), default="waiting")
    
    extracted_text = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    meta_info = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    form = relationship("Form", back_populates="attachments")
