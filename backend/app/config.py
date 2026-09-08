import os
import json
import logging
from pydantic_settings import BaseSettings
from typing import Optional, List, Union

logger = logging.getLogger("formmind.config")

# Detect Vercel / AWS Lambda Serverless execution environment
IS_VERCEL = bool(os.getenv("VERCEL") == "1" or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))

def _get_default_database_url() -> str:
    raw_url = os.getenv("DATABASE_URL")
    if raw_url:
        # Normalize legacy postgres:// to postgresql:// for SQLAlchemy 2.0
        if raw_url.startswith("postgres://"):
            return raw_url.replace("postgres://", "postgresql://", 1)
        return raw_url
    
    # In Vercel serverless, SQLite must live in /tmp since root FS is read-only
    if IS_VERCEL:
        return "sqlite:////tmp/formmind.db"
    return "sqlite:///./formmind.db"

def _get_default_storage_dir(subdir: str) -> str:
    if IS_VERCEL:
        return os.path.join("/tmp", subdir)
    return os.path.join(os.getcwd(), subdir)

class Settings(BaseSettings):
    PROJECT_NAME: str = "FormMind AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production" if IS_VERCEL else "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes") and not IS_VERCEL
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "formmind-ai-super-secret-production-key-change-in-prod-2026")
    SUPABASE_JWT_SECRET: Optional[str] = os.getenv("SUPABASE_JWT_SECRET", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://form-mind-ai-agent.vercel.app",
        "https://formmind-ai.vercel.app"
    ]
    CORS_ORIGIN_REGEX: str = r"https://.*\.vercel\.app"
    
    # Database
    DATABASE_URL: str = _get_default_database_url()
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # Rate Limiting & Upload Protection
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "180"))
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "30"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

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
    UPLOAD_DIR: str = _get_default_storage_dir("uploads")
    EXPORTS_DIR: str = _get_default_storage_dir("exports")

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

# Parse custom CORS_ORIGINS from environment if provided as string or json
raw_cors = os.getenv("CORS_ORIGINS")
settings = Settings()

if raw_cors:
    try:
        if raw_cors.startswith("["):
            settings.CORS_ORIGINS = json.loads(raw_cors)
        else:
            settings.CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
    except Exception:
        pass

# Ensure storage directories exist safely
try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.EXPORTS_DIR, exist_ok=True)
except Exception as e:
    logger.warning(f"Could not initialize upload/export directories: {e}")

# Warn if using default secret key in production
if settings.ENVIRONMENT == "production" and "change-in-prod" in settings.SECRET_KEY:
    logger.warning(
        "⚠️ PRODUCTION SECURITY WARNING: You are running with the default SECRET_KEY. "
        "Please generate a secure random key and set SECRET_KEY in your production environment variables!"
    )
