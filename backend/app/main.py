import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base, init_db_schema, check_db_connectivity
import app.models # Register all models
from app.utils.logging_config import setup_logging
from app.utils.middlewares import (
    RequestIDAndLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimiterMiddleware,
    UploadLimitMiddleware
)
from app.utils.error_handlers import register_error_handlers

# Initialize structured logging
setup_logging()
logger = logging.getLogger("formmind.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schema & ensure required directories
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]...")
    try:
        init_db_schema()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database schema on startup: {e}")
    yield
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FormMind AI — Production API for AI-Powered Google Form Analysis & Intelligence",
    docs_url="/docs" if not settings.ENVIRONMENT == "production" or settings.DEBUG else "/docs",
    redoc_url="/redoc" if not settings.ENVIRONMENT == "production" or settings.DEBUG else None,
    lifespan=lifespan
)

# 1. Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# 2. Upload Limit Middleware
app.add_middleware(UploadLimitMiddleware)

# 3. Rate Limiter Middleware
app.add_middleware(RateLimiterMiddleware)

# 4. Request ID & Logging Middleware
app.add_middleware(RequestIDAndLoggingMiddleware)

# 5. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"]
)

# Register RFC 7807 Error Handlers
register_error_handlers(app)

# Include API Routers
from app.api.auth import router as auth_router
from app.api.forms import router as forms_router
from app.api.chat import router as chat_router
from app.api.exports import router as exports_router

# Mount API Routers under /api
app.include_router(auth_router, prefix="/api")
app.include_router(forms_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(exports_router, prefix="/api")

# Mount without prefix for seamless backwards compatibility
app.include_router(auth_router)
app.include_router(forms_router)
app.include_router(chat_router)
app.include_router(exports_router)

# Health & Observability Probes
@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER
    }

@app.get("/health/live", tags=["Health"])
def liveness_probe():
    return {"status": "alive"}

@app.get("/health/ready", tags=["Health"])
def readiness_probe():
    db_ok = check_db_connectivity()
    if db_ok:
        return {
            "status": "ready",
            "database": "connected",
            "storage": "ready"
        }
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "unhealthy",
            "database": "disconnected",
            "detail": "Database connection verification failed."
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)
