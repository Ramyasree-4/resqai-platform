"""
ResQAI – LangSmith Observability Tracer  (production-grade)

Traces every AI call to LangSmith project "ResQAI" with:
  - Run name & operation type
  - Full prompt (truncated to 4 000 chars for storage)
  - Model name  (mistral-large-latest | gemini-1.5-pro | rule-based-fallback)
  - Raw response (truncated to 2 000 chars)
  - Latency (ms)
  - Token usage  (prompt / completion / total)
  - Retry count
  - Fallback event  (was Gemini used? why?)
  - Error message  (if any)
  - Custom tags:  ResQAI, <model>, <operation>
  - Metadata:    incident_id, district, incident_type, environment

env vars required:
  LANGSMITH_API_KEY  or  LANGCHAIN_API_KEY
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_PROJECT=ResQAI
  LANGCHAIN_ENDPOINT=https://api.smith.langchain.com  (default)
"""

from __future__ import annotations

import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

# Ensure .env is loaded regardless of CWD
try:
    from dotenv import load_dotenv as _load_dotenv
    _load_dotenv(Path(__file__).parent.parent.parent / ".env", override=False)
except ImportError:
    pass

from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Module-level state ────────────────────────────────────────────────────────
_LANGSMITH_AVAILABLE: bool = False
_client = None               # langsmith.Client instance
_project: str = "ResQAI"
_environment: str = os.getenv("ENVIRONMENT", "development")


# ── Initialisation ─────────────────────────────────────────────────────────────

def _resolve_api_key() -> Optional[str]:
    val = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY") or ""
    # Reject placeholder values
    if val.lower().startswith(("your-", "change-", "test")):
        return None
    return val or None


def _is_tracing_enabled() -> bool:
    val = os.getenv("LANGCHAIN_TRACING_V2", "false").strip().lower()
    return val in ("true", "1", "yes")


def init_langsmith() -> bool:
    """
    Initialise LangSmith client.
    Called once at startup. Returns True if tracing is active.
    Safe to call multiple times — idempotent.
    """
    global _LANGSMITH_AVAILABLE, _client, _project

    _project = os.getenv("LANGCHAIN_PROJECT", "ResQAI")
    api_key = _resolve_api_key()
    tracing = _is_tracing_enabled()

    if not tracing:
        logger.info(
            "LangSmith tracing DISABLED — set LANGCHAIN_TRACING_V2=true to enable",
            project=_project,
        )
        return False

    if not api_key:
        logger.warning(
            "LangSmith tracing requested but no API key found",
            hint="Set LANGSMITH_API_KEY or LANGCHAIN_API_KEY",
        )
        return False

    try:
        from langsmith import Client as LangSmithClient  # type: ignore[import]

        _client = LangSmithClient(
            api_url=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
            api_key=api_key,
        )

        # Ensure the project exists — with short timeout, non-blocking
        try:
            import threading
            def _create_project():
                try:
                    existing = [p.name for p in _client.list_projects()]
                    if _project not in existing:
                        _client.create_project(_project, description="ResQAI Disaster Response AI")
                except Exception:
                    pass
            t = threading.Thread(target=_create_project, daemon=True)
            t.start()
            # Don't wait — fire and forget
        except Exception:
            pass

        _LANGSMITH_AVAILABLE = True
        logger.info(
            "LangSmith tracing ENABLED",
            project=_project,
            endpoint=os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
            environment=_environment,
        )
        return True

    except ImportError:
        logger.warning(
            "langsmith package not installed — pip install langsmith",
        )
        return False
    except Exception as e:
        logger.warning(
            "LangSmith init failed — tracing disabled",
            error=str(e),
        )
        return False


# Run init on module import (non-blocking — errors are caught)
init_langsmith()


# ── AITrace  ──────────────────────────────────────────────────────────────────

class AITrace:
    """
    Context manager that records a single AI call as a LangSmith Run.

    Captures:
      - Prompt text (inputs.prompt)
      - Model name  (inputs.model)
      - Raw response (outputs.response)
      - Latency ms  (outputs.latency_ms)
      - Token usage  (outputs.token_usage)
      - Retry count  (outputs.retry_count)
      - Fallback info (outputs.fallback_triggered, outputs.fallback_reason)
      - Error text   (error field on Run)
      - Tags         [ResQAI, <model>, <operation>, <environment>]
      - Metadata     {incident_id, district, incident_type, …}

    Usage::
        with AITrace("analyze_incident", "mistral-large-latest",
                     incident_id="INC-2024-ABC") as trace:
            result = call_model(prompt)
            trace.set_response(str(result))
            trace.set_tokens(prompt_tokens=512, completion_tokens=256)
    """

    def __init__(
        self,
        operation: str,
        model: str,
        incident_id: Optional[str] = None,
        prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.operation = operation
        self.model = model
        self.incident_id = incident_id
        self.prompt = prompt
        self.metadata: Dict[str, Any] = metadata or {}

        # Internal
        self.run_id: str = str(uuid.uuid4())
        self._wall_start: float = time.perf_counter()
        self._utc_start: datetime = datetime.now(timezone.utc)
        self._run_obj = None          # langsmith Run object

        # Mutable state — set by caller
        self.retry_count: int = 0
        self.fallback_triggered: bool = False
        self.fallback_reason: Optional[str] = None
        self.error_message: Optional[str] = None
        self.response_text: Optional[str] = None
        self.token_usage: Dict[str, int] = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    # ── Mutation helpers called by AI services ────────────────────────────

    def set_retry(self, count: int) -> None:
        """Record the current retry attempt number."""
        self.retry_count = count

    def set_fallback(self, reason: str) -> None:
        """Signal that a fallback to the secondary model was triggered."""
        self.fallback_triggered = True
        self.fallback_reason = reason
        logger.info(
            "AI fallback triggered",
            operation=self.operation,
            reason=reason,
            incident_id=self.incident_id,
        )

    def set_response(self, response: str) -> None:
        """Store raw model response (truncated for LangSmith storage)."""
        self.response_text = (response or "")[:2000]

    def set_tokens(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> None:
        """Record token usage from the model response."""
        self.token_usage = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        }

    def set_error(self, error: str) -> None:
        """Record an error message."""
        self.error_message = str(error)[:500]

    # ── Context manager protocol ──────────────────────────────────────────

    def __enter__(self) -> "AITrace":
        if not (_LANGSMITH_AVAILABLE and _client):
            return self

        try:
            tags: List[str] = [
                "ResQAI",
                self.model,
                self.operation,
                _environment,
            ]
            if self.fallback_triggered:
                tags.append("fallback")

            run_metadata: Dict[str, Any] = {
                "incident_id": self.incident_id or "",
                "model": self.model,
                "operation": self.operation,
                "environment": _environment,
                "project": _project,
                **self.metadata,
            }

            self._run_obj = _client.create_run(
                id=self.run_id,
                name=f"resqai.{self.operation}",
                run_type="llm",
                project_name=_project,
                inputs={
                    "prompt": (self.prompt or "")[:4000],
                    "model": self.model,
                    "incident_id": self.incident_id or "",
                    "operation": self.operation,
                },
                extra={
                    "metadata": run_metadata,
                    "tags": tags,
                },
                start_time=self._utc_start,
            )
        except Exception as e:
            # Never crash the application because of tracing
            logger.debug("LangSmith run creation failed", error=str(e))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        elapsed_ms: float = round((time.perf_counter() - self._wall_start) * 1000, 2)
        utc_end = datetime.now(timezone.utc)

        # Capture uncaught exception
        if exc_type is not None:
            self.set_error(str(exc_val))

        # ── structlog entry (always, regardless of LangSmith) ────────────
        log_payload: Dict[str, Any] = {
            "operation": self.operation,
            "model": self.model,
            "latency_ms": elapsed_ms,
            "retry_count": self.retry_count,
            "fallback_triggered": self.fallback_triggered,
            "fallback_reason": self.fallback_reason,
            "tokens_total": self.token_usage["total_tokens"],
            "tokens_prompt": self.token_usage["prompt_tokens"],
            "tokens_completion": self.token_usage["completion_tokens"],
            "incident_id": self.incident_id,
        }
        if self.error_message:
            log_payload["error"] = self.error_message
            logger.error("AI call FAILED", **log_payload)
        else:
            logger.info("AI call COMPLETE", **log_payload)

        # ── LangSmith run update ──────────────────────────────────────────
        if _LANGSMITH_AVAILABLE and _client and self._run_obj:
            try:
                outputs: Dict[str, Any] = {
                    "response": self.response_text or "",
                    "latency_ms": elapsed_ms,
                    "retry_count": self.retry_count,
                    "fallback_triggered": self.fallback_triggered,
                    "fallback_reason": self.fallback_reason or "",
                    "token_usage": self.token_usage,
                    "ai_confidence": self.metadata.get("confidence"),
                    "severity": self.metadata.get("severity"),
                }

                update_kwargs: Dict[str, Any] = {
                    "outputs": outputs,
                    "end_time": utc_end,
                    "extra": {
                        "metadata": {
                            "latency_ms": elapsed_ms,
                            "retry_count": self.retry_count,
                            "fallback_triggered": self.fallback_triggered,
                            "token_total": self.token_usage["total_tokens"],
                        }
                    },
                }
                if self.error_message:
                    update_kwargs["error"] = self.error_message

                _client.update_run(self.run_id, **update_kwargs)

            except Exception as e:
                logger.debug("LangSmith run update failed", error=str(e))

        return False   # never suppress exceptions


# ── Public context manager ────────────────────────────────────────────────────

@contextmanager
def trace_ai_call(
    operation: str,
    model: str,
    incident_id: Optional[str] = None,
    prompt: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Generator[AITrace, None, None]:
    """
    Context manager for tracing a single AI operation in LangSmith.

    Transparent no-op when LangSmith is disabled or unavailable —
    the rest of the application never needs to check.

    Args:
        operation:   Name of the AI operation  (e.g. "analyze_incident")
        model:       Model identifier           (e.g. "mistral-large-latest")
        incident_id: ResQAI incident ID for correlation
        prompt:      Full prompt text (truncated before upload)
        metadata:    Extra key/value pairs attached to the Run

    Usage::
        with trace_ai_call(
            "analyze_incident",
            "mistral-large-latest",
            incident_id="INC-2024-ABCD1234",
            prompt=prompt_text,
            metadata={"district": "Khurda", "incident_type": "FLOOD"},
        ) as trace:
            result, error, retries = mistral_service.analyze(prompt)
            trace.set_response(str(result))
            trace.set_retry(retries)
            if error:
                trace.set_error(error)
    """
    trace = AITrace(
        operation=operation,
        model=model,
        incident_id=incident_id,
        prompt=prompt,
        metadata=metadata,
    )
    with trace:
        yield trace


# ── Convenience decorator ──────────────────────────────────────────────────────

def langsmith_trace(
    operation: Optional[str] = None,
    model: str = "unknown",
    tags: Optional[List[str]] = None,
):
    """
    Decorator to trace a function call in LangSmith.

    Usage::
        @langsmith_trace(operation="classify_incident", model="mistral-large-latest")
        def classify(incident_data: dict) -> dict:
            ...
    """
    import functools

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            op_name = operation or fn.__name__
            with trace_ai_call(op_name, model, metadata={"tags": tags or []}):
                return fn(*args, **kwargs)
        return wrapper
    return decorator


# ── Status helpers ────────────────────────────────────────────────────────────

def langsmith_status() -> Dict[str, Any]:
    """Return current LangSmith connection status for health checks."""
    return {
        "enabled": _LANGSMITH_AVAILABLE,
        "project": _project if _LANGSMITH_AVAILABLE else None,
        "endpoint": os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        "tracing_v2": _is_tracing_enabled(),
        "has_api_key": bool(_resolve_api_key()),
    }
