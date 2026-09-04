import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON, DateTime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from app.database import Base

class FormResponse(Base):
    __tablename__ = "form_responses"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    google_response_id = Column(String(255), nullable=True, index=True)
    response_number = Column(Integer, default=1)
    submission_timestamp = Column(DateTime, nullable=True)
    
    # Store complete raw row snapshot & complete cleaned row snapshot
    raw_data = Column(JSON, default=dict)       # {"Timestamp": "...", "Question 1": "..."}
    cleaned_data = Column(JSON, default=dict)   # {"Q1": 4.0, "Q2": "Python", "Q3": ["Option A", "Option B"]}
    is_valid = Column(Boolean, default=True)    # False if completely empty / dropped during cleaning
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    form = relationship("Form", back_populates="responses")
    answers = relationship("ResponseAnswer", back_populates="response", cascade="all, delete-orphan")


class ResponseAnswer(Base):
    __tablename__ = "response_answers"

    id = Column(String(64), primary_key=True, index=True)
    response_id = Column(String(64), ForeignKey("form_responses.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(64), ForeignKey("form_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    raw_value = Column(Text, nullable=True)
    cleaned_value = Column(Text, nullable=True)
    parsed_json_value = Column(JSON, nullable=True)  # For arrays (multiselect), structured numbers, etc.
    
    response = relationship("FormResponse", back_populates="answers")
    question = relationship("FormQuestion", back_populates="answers")
