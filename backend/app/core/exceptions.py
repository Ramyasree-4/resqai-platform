"""
ResQAI – Custom Exception Hierarchy
All application-specific exceptions inherit from ResQAIException.
"""
from typing import Any, Dict, Optional


class ResQAIException(Exception):
    """Base exception for all ResQAI errors."""
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.__class__.message
        self.error_code = error_code or self.__class__.error_code
        self.details = details or {}
        super().__init__(self.message)


# ── 400 Bad Request ────────────────────────────────────────────────────────────
class ValidationError(ResQAIException):
    status_code = 400
    error_code = "VALIDATION_ERROR"
    message = "Request validation failed."


class InvalidCoordinatesError(ValidationError):
    error_code = "INVALID_COORDINATES"
    message = "Latitude must be -90 to 90 and longitude -180 to 180."


class FileTooLargeError(ValidationError):
    error_code = "FILE_TOO_LARGE"
    message = "Uploaded file exceeds the maximum allowed size."


class InvalidFileTypeError(ValidationError):
    error_code = "INVALID_FILE_TYPE"
    message = "File type is not allowed."


# ── 401 Unauthorized ───────────────────────────────────────────────────────────
class AuthenticationError(ResQAIException):
    status_code = 401
    error_code = "AUTHENTICATION_FAILED"
    message = "Authentication failed. Please login again."


class TokenExpiredError(AuthenticationError):
    error_code = "TOKEN_EXPIRED"
    message = "Your session has expired. Please login again."


class InvalidTokenError(AuthenticationError):
    error_code = "INVALID_TOKEN"
    message = "Invalid authentication token."


# ── 403 Forbidden ─────────────────────────────────────────────────────────────
class PermissionDeniedError(ResQAIException):
    status_code = 403
    error_code = "PERMISSION_DENIED"
    message = "You do not have permission to perform this action."


class InsufficientRoleError(PermissionDeniedError):
    error_code = "INSUFFICIENT_ROLE"
    message = "Your role does not have access to this resource."


# ── 404 Not Found ─────────────────────────────────────────────────────────────
class NotFoundError(ResQAIException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found."


class IncidentNotFoundError(NotFoundError):
    error_code = "INCIDENT_NOT_FOUND"
    message = "The requested incident does not exist."


class ResourceNotFoundError(NotFoundError):
    error_code = "RESOURCE_NOT_FOUND"
    message = "The requested resource does not exist."


class UserNotFoundError(NotFoundError):
    error_code = "USER_NOT_FOUND"
    message = "User not found."


# ── 409 Conflict ──────────────────────────────────────────────────────────────
class ConflictError(ResQAIException):
    status_code = 409
    error_code = "CONFLICT"
    message = "A conflict occurred with the current state of the resource."


class DuplicateEmailError(ConflictError):
    error_code = "DUPLICATE_EMAIL"
    message = "An account with this email already exists."


# ── 422 Unprocessable ─────────────────────────────────────────────────────────
class UnprocessableError(ResQAIException):
    status_code = 422
    error_code = "UNPROCESSABLE"
    message = "The request could not be processed."


# ── 429 Rate Limited ──────────────────────────────────────────────────────────
class RateLimitError(ResQAIException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Too many requests. Please slow down."


# ── 500 Server Errors ─────────────────────────────────────────────────────────
class FirebaseError(ResQAIException):
    status_code = 500
    error_code = "FIREBASE_ERROR"
    message = "A database error occurred. Please try again."


class GeminiError(ResQAIException):
    status_code = 500
    error_code = "AI_SERVICE_ERROR"
    message = "The AI service is temporarily unavailable."


class GeminiTimeoutError(GeminiError):
    error_code = "AI_TIMEOUT"
    message = "AI analysis timed out. Please try again."


class GeminiCircuitOpenError(GeminiError):
    status_code = 503
    error_code = "AI_CIRCUIT_OPEN"
    message = "AI service is temporarily suspended due to repeated failures."


class StorageError(ResQAIException):
    status_code = 500
    error_code = "STORAGE_ERROR"
    message = "File storage operation failed."


# ── 503 Service Unavailable ───────────────────────────────────────────────────
class ServiceUnavailableError(ResQAIException):
    status_code = 503
    error_code = "SERVICE_UNAVAILABLE"
    message = "Service is temporarily unavailable. Please try again later."
