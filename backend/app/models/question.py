from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class FormQuestion(Base):
    __tablename__ = "form_questions"

    id = Column(String(64), primary_key=True, index=True)
    form_id = Column(String(64), ForeignKey("forms.id", ondelete="CASCADE"), nullable=False, index=True)
    question_key = Column(String(64), nullable=False)  # e.g., Q1, Q2 or question ID
    question_index = Column(Integer, default=0)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), default="multiple_choice") 
    # Types: multiple_choice, checkboxes, dropdown, linear_scale, rating, short_answer, paragraph, yes_no, date, time, other
    options = Column(JSON, default=list)  # list of option strings
    is_required = Column(Boolean, default=False)
    
    # Inferred data characteristics
    inferred_data_type = Column(String(50), default="categorical")  # numeric, categorical, text, boolean, multiselect, date
    scale_min = Column(Integer, nullable=True)
    scale_max = Column(Integer, nullable=True)

    form = relationship("Form", back_populates="questions")
    answers = relationship("ResponseAnswer", back_populates="question", cascade="all, delete-orphan")
