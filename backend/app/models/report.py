import datetime
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(50), default="full")  # full, executive_summary, one_page, five_page, negative_feedback, leadership
    title = Column(String(255), nullable=False)
    content_markdown = Column(Text, nullable=False)
    structure_json = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    form = relationship("Form", back_populates="generated_reports")


class GeneratedFile(Base):
    __tablename__ = "generated_files"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    file_type = Column(String(20), nullable=False)  # pdf, docx, xlsx, csv, png, jpg
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    download_url = Column(String(500), nullable=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    form = relationship("Form", back_populates="generated_files")
