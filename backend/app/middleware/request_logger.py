"""
ResQAI – Request / Response Logging Middleware
Logs every request with timing, method, path, status, and request ID.
"""
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.context import set_request_id
from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a request ID and logs request/response pairs."""

    SKIP_PATHS = {"/health", "/metrics", "/favicon.ico"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Assign unique request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        set_request_id(request_id)

        path = request.url.path
        skip = path in self.SKIP_PATHS

        if not skip:
            logger.info(
                "Request started",
                method=request.method,
                path=path,
                query=str(request.query_params),
                client=request.client.host if request.client else "unknown",
                request_id=request_id,
            )

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        # Attach request ID to response headers
        response.headers["X-Request-ID"] = request_id

        if not skip:
            level = "warning" if response.status_code >= 400 else "info"
            log_fn = getattr(logger, level)
            log_fn(
                "Request completed",
                method=request.method,
                path=path,
                status=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id,
            )

        return response
