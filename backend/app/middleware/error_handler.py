"""
ResQAI – Global Exception Handler Middleware
Converts all exceptions to the standard error envelope format.
"""
import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.context import get_request_id
from app.core.exceptions import ResQAIException
from app.core.logging import get_logger

logger = get_logger(__name__)


def _make_error_body(
    error_code: str,
    message: str,
    status_code: int,
    details=None,
) -> dict:
    body = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "statusCode": status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requestId": get_request_id() or "unknown",
        },
    }
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""

    @app.exception_handler(ResQAIException)
    async def resqai_exception_handler(request: Request, exc: ResQAIException):
        logger.warning(
            "Application exception",
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_make_error_body(
                exc.error_code,
                exc.message,
                exc.status_code,
                exc.details or None,
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Build user-friendly field error list
        field_errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"])
            field_errors.append({"field": field, "message": error["msg"]})

        logger.warning(
            "Request validation failed",
            path=str(request.url),
            errors=field_errors,
        )
        return JSONResponse(
            status_code=422,
            content=_make_error_body(
                "VALIDATION_ERROR",
                "Request validation failed. Check field errors.",
                422,
                {"fields": field_errors},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_make_error_body(
                "HTTP_ERROR",
                str(exc.detail),
                exc.status_code,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled exception",
            error=str(exc),
            traceback=traceback.format_exc(),
            path=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content=_make_error_body(
                "INTERNAL_ERROR",
                "An unexpected error occurred. Please try again later.",
                500,
            ),
        )
