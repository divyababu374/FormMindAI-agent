import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ConnectedAccount(Base):
    __tablename__ = "connected_accounts"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), default="google")  # google, microsoft
    email = Column(String(255), index=True, nullable=False)
    name = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    access_token = Column(String(1024), nullable=True)
    refresh_token = Column(String(1024), nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    meta_data = Column(JSON, default=dict)
    connected_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="connected_accounts")


class ConnectedDriveForm(Base):
    __tablename__ = "connected_drive_forms"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    connected_email = Column(String(255), index=True, nullable=False)
    google_form_id = Column(String(255), index=True, nullable=False)
    title = Column(String(500), nullable=False)
    edit_url = Column(String(1000), nullable=True)
    view_url = Column(String(1000), nullable=True)
    created_time = Column(String(100), nullable=True)
    modified_time = Column(String(100), nullable=True)
    is_imported = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User")
