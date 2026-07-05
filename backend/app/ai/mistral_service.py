"""
ResQAI – Mistral AI Service (Primary LLM)
"""
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Ensure .env is loaded regardless of CWD
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(Path(__file__).parent.parent.parent / ".env", override=False)
except ImportError:
    pass

from app.core.logging import get_logger
from app.ai.json_parser import parse_llm_json
from app.ai.response_validator import (
    validate_standard_response,
    normalise_standard_response,
    build_fallback_standard_response,
)

logger = get_logger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
MISTRAL_TIMEOUT = int(os.getenv("MISTRAL_TIMEOUT_SECONDS", "30"))
MISTRAL_MAX_RETRIES = int(os.getenv("MISTRAL_MAX_RETRIES", "3"))

# Detect placeholder values — treat as missing
_PLACEHOLDER_PREFIXES = ("your-", "change-", "test-key", "")
def _is_real_key(val: str) -> bool:
    """Return True only if val looks like a real API key, not a placeholder."""
    if not val:
        return False
    lower = val.lower()
    return not any(lower.startswith(p) for p in ("your-", "change-", "sk-placeholder", "test"))

_MISTRAL_KEY_VALID = _is_real_key(MISTRAL_API_KEY)

# Errors that should trigger fallback to Gemini (not retried)
FALLBACK_TRIGGER_ERRORS = {
    "status_code_429",   # Rate limit
    "status_code_500",
    "status_code_502",
    "status_code_503",
    "status_code_504",
    "timeout",
    "connection_error",
    "quota_exceeded",
}


class MistralCircuitBreaker:
    """Per-service circuit breaker for Mistral API."""

    def __init__(self, threshold: int = 5, reset_timeout: int = 120):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self._failures = 0
        self._opened_at: Optional[float] = None

    @property
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if time.time() - self._opened_at > self.reset_timeout:
            self._failures = 0
            self._opened_at = None
            logger.info("Mistral circuit breaker HALF-OPEN — probing")
            return False
        return True

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = time.time()
            logger.warning(
                "Mistral circuit breaker OPENED",
                failures=self._failures,
                threshold=self.threshold,
            )

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None


_mistral_circuit = MistralCircuitBreaker(threshold=5, reset_timeout=120)


class MistralService:
    """
    Mistral AI service with:
    - Retry with exponential backoff (up to MISTRAL_MAX_RETRIES times)
    - Timeout protection
    - Rate limit detection
    - JSON mode output
    - Circuit breaker
    """

    def __init__(self):
        if not MISTRAL_API_KEY or not _MISTRAL_KEY_VALID:
            logger.warning("MISTRAL_API_KEY not set or is a placeholder — Mistral service disabled")
            self._client = None
            return

        try:
            from mistralai import Mistral
            self._client = Mistral(api_key=MISTRAL_API_KEY)
            logger.info("MistralService initialized", model=MISTRAL_MODEL)
        except ImportError:
            logger.warning("mistralai package not installed — Mistral service disabled")
            self._client = None
        except Exception as e:
            logger.error("Mistral client init failed", error=str(e))
            self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None and not _mistral_circuit.is_open

    def _call_with_retry(
        self,
        messages: List[Dict[str, str]],
        json_mode: bool = True,
        trace=None,
    ) -> Tuple[Optional[str], Optional[str], int]:
        """
        Call Mistral with retry logic.
        Returns (raw_text, error_message, retry_count).
        """
        if not self._client:
            return None, "Mistral client not initialized", 0

        last_error = None
        retry_count = 0
        backoff = 2  # seconds

        for attempt in range(MISTRAL_MAX_RETRIES):
            retry_count = attempt
            if trace:
                trace.set_retry(attempt)

            try:
                kwargs: Dict[str, Any] = {
                    "model": MISTRAL_MODEL,
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 2048,
                    "top_p": 0.9,
                    "timeout_ms": MISTRAL_TIMEOUT * 1000,
                }
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self._client.chat.complete(**kwargs)

                if not response or not response.choices:
                    last_error = "Empty response from Mistral"
                    logger.warning("Mistral empty response", attempt=attempt + 1)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue

                raw_text = response.choices[0].message.content

                # Capture token usage if available
                if trace and hasattr(response, "usage") and response.usage:
                    trace.set_tokens(
                        prompt_tokens=getattr(response.usage, "prompt_tokens", 0),
                        completion_tokens=getattr(response.usage, "completion_tokens", 0),
                    )

                _mistral_circuit.record_success()
                logger.info(
                    "Mistral call succeeded",
                    attempt=attempt + 1,
                    model=MISTRAL_MODEL,
                    response_length=len(raw_text) if raw_text else 0,
                )
                return raw_text, None, retry_count

            except Exception as e:
                error_str = str(e).lower()
                last_error = str(e)

                # Detect rate limit / server errors → trigger fallback immediately
                is_rate_limit = any(code in error_str for code in ["429", "rate_limit", "quota"])
                is_server_error = any(code in error_str for code in ["500", "502", "503", "504"])
                is_timeout = any(w in error_str for w in ["timeout", "timed out", "connection"])

                if is_rate_limit or is_server_error or is_timeout:
                    logger.warning(
                        "Mistral permanent error — triggering fallback",
                        error=last_error,
                        attempt=attempt + 1,
                    )
                    _mistral_circuit.record_failure()
                    return None, f"FALLBACK_TRIGGER: {last_error}", retry_count

                logger.warning(
                    "Mistral call failed — retrying",
                    error=last_error,
                    attempt=attempt + 1,
                    retry_in=backoff,
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)

        _mistral_circuit.record_failure()
        return None, f"Mistral failed after {MISTRAL_MAX_RETRIES} attempts: {last_error}", retry_count

    def analyze_incident(
        self,
        prompt: str,
        incident_id: Optional[str] = None,
        trace=None,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """
        Analyze an incident using Mistral.
        Returns (result_dict, error_message, retry_count).
        """
        if not self.is_available:
            reason = "circuit_open" if _mistral_circuit.is_open else "client_unavailable"
            return None, f"Mistral unavailable: {reason}", 0

        messages = [
            {
                "role": "system",
                "content": (
                    "You are ResQAI, an AI disaster response analysis system. "
                    "Always respond with valid JSON only. "
                    "Never include markdown, explanations, or code fences."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        raw_text, error, retry_count = self._call_with_retry(
            messages, json_mode=True, trace=trace
        )

        if error:
            return None, error, retry_count

        if not raw_text:
            return None, "Empty response from Mistral", retry_count

        if trace:
            trace.set_response(raw_text)

        # Parse JSON
        parsed, parse_error = parse_llm_json(raw_text)
        if parse_error or not parsed:
            logger.warning("Mistral JSON parse failed", error=parse_error)
            # Attempt schema correction via another call
            correction_result, corr_error, corr_retries = self._attempt_correction(raw_text, trace)
            if correction_result:
                return correction_result, None, retry_count + corr_retries
            return None, f"Mistral JSON invalid: {parse_error}", retry_count

        # Normalise and validate
        normalised = normalise_standard_response(parsed)
        is_valid, errors = validate_standard_response(normalised)

        if not is_valid:
            logger.warning("Mistral response schema invalid", errors=errors)
            correction_result, corr_error, corr_retries = self._attempt_correction(raw_text, trace)
            if correction_result:
                return correction_result, None, retry_count + corr_retries
            return None, f"Mistral schema invalid: {errors}", retry_count

        logger.info(
            "Mistral analysis complete",
            incident_id=incident_id,
            severity=normalised.get("severity"),
            confidence=normalised.get("confidence"),
            retry_count=retry_count,
        )
        return normalised, None, retry_count

    def _attempt_correction(
        self, bad_response: str, trace=None
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], int]:
        """Ask Mistral to self-correct invalid JSON output."""
        from app.ai.prompt_templates import build_schema_correction_prompt
        correction_prompt = build_schema_correction_prompt(bad_response)
        messages = [
            {"role": "system", "content": "Fix the JSON. Return only valid JSON."},
            {"role": "user", "content": correction_prompt},
        ]
        raw, error, retries = self._call_with_retry(messages, json_mode=True)
        if error or not raw:
            return None, error, retries

        parsed, parse_error = parse_llm_json(raw)
        if parse_error or not parsed:
            return None, parse_error, retries

        normalised = normalise_standard_response(parsed)
        is_valid, _ = validate_standard_response(normalised)
        if is_valid:
            return normalised, None, retries
        return None, "Correction attempt failed validation", retries


# ── Singleton ─────────────────────────────────────────────────────────────────
_mistral_service: Optional[MistralService] = None


def get_mistral_service() -> MistralService:
    global _mistral_service
    if _mistral_service is None:
        _mistral_service = MistralService()
    return _mistral_service


def reset_mistral_service() -> None:
    """Force re-initialisation — called if API key changes at runtime."""
    global _mistral_service
    _mistral_service = None
