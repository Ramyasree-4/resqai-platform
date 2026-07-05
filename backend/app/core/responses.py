"""
ResQAI – Standardized API Response Helpers
Every endpoint returns a consistent envelope format.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.context import get_request_id


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200,
) -> Dict[str, Any]:
    """Build a standard success envelope."""
    response: Dict[str, Any] = {"success": True, "data": data}
    if message:
        response["message"] = message
    return response


def created_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    return success_response(data, message, status_code=201)


def error_response(
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Build a standard error JSONResponse."""
    body: Dict[str, Any] = {
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
    return JSONResponse(status_code=status_code, content=body)


def paginated_response(
    items: list,
    total: int,
    page: int,
    limit: int,
) -> Dict[str, Any]:
    """Wrap a list result with pagination metadata."""
    import math
    return {
        "success": True,
        "data": {
            "items": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "totalPages": math.ceil(total / limit) if limit > 0 else 0,
            },
        },
    }
