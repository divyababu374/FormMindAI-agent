import datetime
from sqlalchemy import Column, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class FormAnalysis(Base):
    __tablename__ = "form_analyses"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    executive_summary = Column(Text, nullable=True)
    basic_statistics = Column(JSON, default=dict)
    numerical_analysis = Column(JSON, default=dict)
    categorical_analysis = Column(JSON, default=dict)
    text_analysis = Column(JSON, default=dict)
    comparative_analysis = Column(JSON, default=list)
    ai_insights = Column(JSON, default=dict)
    
    # Provider metadata used for analysis
    ai_provider_used = Column(String(50), default="smart_engine")
    model_name_used = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    form = relationship("Form", back_populates="analysis")
