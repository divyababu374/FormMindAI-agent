import time
import uuid
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from app.config import settings

logger = logging.getLogger("formmind.middleware")

class RequestIDAndLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = req_id
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # Avoid log spam for health checks in production
        if not request.url.path.startswith("/health") and not request.url.path == "/":
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                f"[{req_id[:8]}] {request.method} {request.url.path} - {response.status_code} ({duration_ms}ms) [{client_ip}]"
            )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # HSTS only in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_records = defaultdict(list)
        self.last_cleanup = time.time()

    def _cleanup_old_records(self, now: float):
        if now - self.last_cleanup > 60:
            for ip in list(self.request_records.keys()):
                self.request_records[ip] = [t for t in self.request_records[ip] if now - t < 60]
                if not self.request_records[ip]:
                    del self.request_records[ip]
            self.last_cleanup = now

    async def dispatch(self, request: Request, call_next):
        # Exclude health check and docs from rate limits
        path = request.url.path
        if path in ("/", "/health", "/health/live", "/health/ready", "/api/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip and request.client:
            client_ip = request.client.host
        if not client_ip:
            client_ip = "127.0.0.1"

        # Bypass rate limiting in testing environment or for pytest testclient
        if settings.ENVIRONMENT == "testing" or client_ip == "testclient":
            return await call_next(request)

        now = time.time()
        self._cleanup_old_records(now)

        timestamps = self.request_records[client_ip]
        recent_timestamps = [t for t in timestamps if now - t < 60]
        self.request_records[client_ip] = recent_timestamps

        # Determine limit for path
        is_auth = "/auth/" in path
        limit = settings.RATE_LIMIT_AUTH_PER_MINUTE if is_auth else settings.RATE_LIMIT_PER_MINUTE

        if len(recent_timestamps) >= limit:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {path} ({len(recent_timestamps)} requests/min)")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too Many Requests",
                    "detail": f"Rate limit of {limit} requests per minute exceeded. Please try again later.",
                    "retry_after_seconds": 30
                },
                headers={"Retry-After": "30"}
            )

        self.request_records[client_ip].append(now)
        return await call_next(request)


class UploadLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        if content_length and int(content_length) > max_bytes:
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Payload Too Large",
                    "detail": f"Uploaded payload exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
                }
            )

        return await call_next(request)
