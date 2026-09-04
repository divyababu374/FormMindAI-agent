import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Form(Base):
    __tablename__ = "forms"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source_url = Column(String(1000), nullable=True)
    source_type = Column(String(50), default="google_form")  # google_form, google_sheet, file_upload, demo
    google_form_id = Column(String(255), nullable=True)
    google_sheet_id = Column(String(255), nullable=True)
    
    total_responses_count = Column(Integer, default=0)
    questions_count = Column(Integer, default=0)
    completion_rate = Column(String(20), default="100%")
    status = Column(String(50), default="completed")  # pending, processing, completed, failed
    status_message = Column(String(255), nullable=True)
    
    # Detailed Data Source & Synchronization Statuses
    form_metadata_status = Column(String(50), default="ready")      # ready, failed
    response_access_status = Column(String(50), default="ready")    # ready, authorized, unauthorized, zero_responses, failed
    response_sync_status = Column(String(50), default="synced")     # synced, pending, syncing, failed
    analysis_status = Column(String(50), default="ready")           # ready, pending, unavailable, failed
    attachment_status = Column(String(50), default="none")          # none, processing, ready, failed
    last_synced_at = Column(DateTime, nullable=True)
    
    # Store schema snapshot / metadata
    meta_info = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="forms")
    questions = relationship("FormQuestion", back_populates="form", cascade="all, delete-orphan", order_by="FormQuestion.question_index")
    responses = relationship("FormResponse", back_populates="form", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="form", cascade="all, delete-orphan")
    analysis = relationship("FormAnalysis", back_populates="form", uselist=False, cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="form", cascade="all, delete-orphan")
    generated_reports = relationship("GeneratedReport", back_populates="form", cascade="all, delete-orphan")
    generated_files = relationship("GeneratedFile", back_populates="form", cascade="all, delete-orphan")
