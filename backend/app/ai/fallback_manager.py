"""
ResQAI – Fallback Manager
Determines when to switch from Mistral to Gemini.
Transparent to the rest of the application.
"""
from enum import Enum
from typing import Any, Dict, Optional


class FallbackReason(str, Enum):
    MISTRAL_TIMEOUT = "mistral_timeout"
    MISTRAL_RATE_LIMIT = "mistral_rate_limit"
    MISTRAL_SERVER_ERROR = "mistral_server_error"
    MISTRAL_INVALID_JSON = "mistral_invalid_json"
    MISTRAL_EMPTY_RESPONSE = "mistral_empty_response"
    MISTRAL_QUOTA_EXCEEDED = "mistral_quota_exceeded"
    MISTRAL_CONNECTION_ERROR = "mistral_connection_error"
    MISTRAL_CIRCUIT_OPEN = "mistral_circuit_open"
    MISTRAL_NOT_AVAILABLE = "mistral_not_available"
    MISTRAL_MAX_RETRIES = "mistral_max_retries"
    UNKNOWN = "unknown"


def should_fallback_to_gemini(error_message: Optional[str]) -> tuple[bool, FallbackReason]:
    """
    Decide if the Mistral error warrants an immediate Gemini fallback.
    Returns (should_fallback: bool, reason: FallbackReason).
    """
    if not error_message:
        return True, FallbackReason.UNKNOWN

    err = error_message.lower()

    # Permanent errors — fallback immediately without further Mistral retries
    if "circuit_open" in err or "circuit breaker" in err:
        return True, FallbackReason.MISTRAL_CIRCUIT_OPEN
    if "not available" in err or "not initialized" in err:
        return True, FallbackReason.MISTRAL_NOT_AVAILABLE
    if "429" in err or "rate_limit" in err or "too many requests" in err:
        return True, FallbackReason.MISTRAL_RATE_LIMIT
    if "quota" in err or "quota_exceeded" in err:
        return True, FallbackReason.MISTRAL_QUOTA_EXCEEDED
    if "500" in err or "502" in err or "503" in err or "504" in err:
        return True, FallbackReason.MISTRAL_SERVER_ERROR
    if "timeout" in err or "timed out" in err:
        return True, FallbackReason.MISTRAL_TIMEOUT
    if "connection" in err or "network" in err:
        return True, FallbackReason.MISTRAL_CONNECTION_ERROR
    if "json" in err or "parse" in err or "invalid" in err:
        return True, FallbackReason.MISTRAL_INVALID_JSON
    if "empty" in err:
        return True, FallbackReason.MISTRAL_EMPTY_RESPONSE
    if "failed after" in err or "max_retries" in err or "fallback_trigger" in err:
        return True, FallbackReason.MISTRAL_MAX_RETRIES

    # All Mistral errors trigger Gemini fallback — fail safe
    return True, FallbackReason.UNKNOWN
