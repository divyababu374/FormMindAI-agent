import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings

logger = logging.getLogger("formmind.errors")

def register_error_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        req_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "detail": exc.detail,
                "status_code": exc.status_code,
                "request_id": req_id
            },
            headers={"X-Request-ID": req_id} if req_id else {}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        req_id = getattr(request.state, "request_id", None)
        errors = []
        for err in exc.errors():
            loc = " -> ".join([str(l) for l in err.get("loc", [])])
            msg = err.get("msg", "Invalid value")
            errors.append(f"{loc}: {msg}")

        detail_msg = "; ".join(errors) if errors else "Invalid request body or parameters."

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "detail": detail_msg,
                "validation_errors": exc.errors(),
                "status_code": 422,
                "request_id": req_id
            },
            headers={"X-Request-ID": req_id} if req_id else {}
        )

    @app.exception_handler(Exception)
    async def global_unhandled_exception_handler(request: Request, exc: Exception):
        req_id = getattr(request.state, "request_id", None)
        logger.exception(f"Unhandled Internal Server Error on {request.method} {request.url.path} [ReqID: {req_id}]: {exc}")
        
        detail_msg = "An unexpected internal server error occurred."
        if settings.DEBUG:
            detail_msg = f"Internal Error: {str(exc)}"

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "detail": detail_msg,
                "status_code": 500,
                "request_id": req_id
            },
            headers={"X-Request-ID": req_id} if req_id else {}
        )
