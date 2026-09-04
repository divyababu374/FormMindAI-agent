import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FormMind AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "formmind-ai-super-secret-production-key-change-in-prod-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./formmind.db")
    
    # Google OAuth & APIs
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: Optional[str] = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5173/auth/callback")
    
    # AI Providers Configuration
    # AI_PROVIDER can be 'auto', 'gemini', 'openai', 'groq', 'ollama', or 'smart'
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "auto")
    AI_API_KEY: Optional[str] = os.getenv("AI_API_KEY", "")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: Optional[str] = os.getenv("MODEL_NAME", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    # File uploads & storage
    UPLOAD_DIR: str = os.path.join(os.getcwd(), "uploads")
    EXPORTS_DIR: str = os.path.join(os.getcwd(), "exports")

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
