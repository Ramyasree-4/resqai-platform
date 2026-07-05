"""
ResQAI – Structured Logging Configuration
structlog with PrintLoggerFactory — works without stdlib integration.
JSON in production, pretty console in development.
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from app.config import get_settings

settings = get_settings()


def _add_request_id(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Inject request_id from context var if present."""
    from app.core.context import get_request_id
    request_id = get_request_id()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def _add_app_info(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add app name and environment to every log entry."""
    event_dict["app"] = settings.APP_NAME
    event_dict["env"] = settings.ENVIRONMENT
    return event_dict


def setup_logging() -> None:
    """Configure structlog for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # NOTE: structlog.stdlib.add_logger_name only works with stdlib logger
    # factory. We use PrintLoggerFactory, so we omit it.
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        # add_logger_name removed — incompatible with PrintLoggerFactory
        structlog.processors.TimeStamper(fmt="iso"),
        _add_request_id,
        _add_app_info,
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.LOG_FORMAT == "json" or settings.is_production:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Stdlib logging (for uvicorn, firebase, httpx)
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("google.auth").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """Return a bound structlog logger."""
    return structlog.get_logger(name)
