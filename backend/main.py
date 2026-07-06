"""
ResQAI – FastAPI Application Entry Point
Production-ready. Render / Cloud Run compatible.

PORT is read from environment variable — Render injects this automatically.
All startup steps have timeouts so the server ALWAYS binds quickly.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import api_router
from app.config import get_settings, settings
from app.core.logging import get_logger, setup_logging
from app.firebase.client import initialize_firebase
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logger import RequestLoggerMiddleware

# ── Logging must be first ─────────────────────────────────────────────────────
setup_logging()
logger = get_logger(__name__)


def _run_with_timeout(fn, timeout: float = 5.0, label: str = "") -> bool:
    """Run a callable in a thread with a timeout. Returns True on success."""
    import threading
    result = {"ok": False, "error": None}

    def _target():
        try:
            fn()
            result["ok"] = True
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=timeout)

    if t.is_alive():
        logger.warning(f"{label} timed out after {timeout}s — continuing startup")
        return False
    if not result["ok"]:
        logger.warning(f"{label} failed: {result['error']}")
        return False
    return True


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    Every step is wrapped with a timeout — the server ALWAYS starts even if
    an external service (Firebase, LangSmith, Mistral) is slow to respond.
    """
    logger.info(
        "ResQAI backend starting",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        port=os.getenv("PORT", str(settings.PORT)),
    )

    # ── Demo Mode vs Firebase ────────────────────────────────────────────
    _demo = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    if _demo:
        logger.info("DEMO_MODE=true — in-memory store active, Firebase skipped")
        from app.demo.store import seed_demo_data
        seed_demo_data()
        logger.info("Demo data seeded")
    else:
        _run_with_timeout(initialize_firebase, timeout=10.0, label="Firebase init")

    # ── Reset AI singletons (pick up fresh env keys) ─────────────────────
    try:
        from app.ai.mistral_service import reset_mistral_service
        from app.ai.gemini_service import reset_gemini_fallback_service
        reset_mistral_service()
        reset_gemini_fallback_service()
    except Exception:
        pass

    # ── Mistral AI ───────────────────────────────────────────────────────
    def _init_mistral():
        from app.ai.mistral_service import get_mistral_service
        svc = get_mistral_service()
        if svc.is_available:
            logger.info("Mistral AI initialized", model=settings.MISTRAL_MODEL)
        else:
            logger.warning("Mistral AI unavailable")

    _run_with_timeout(_init_mistral, timeout=8.0, label="Mistral init")

    # ── Gemini Fallback ──────────────────────────────────────────────────
    def _init_gemini():
        from app.ai.gemini_service import get_gemini_fallback_service
        svc = get_gemini_fallback_service()
        if svc.is_available:
            logger.info("Gemini fallback initialized", model=settings.GEMINI_MODEL)

    _run_with_timeout(_init_gemini, timeout=8.0, label="Gemini fallback init")

    # ── AI Manager ───────────────────────────────────────────────────────
    def _init_ai_manager():
        from app.ai.ai_manager import get_ai_manager
        get_ai_manager()
        logger.info("AI Manager initialized")

    _run_with_timeout(_init_ai_manager, timeout=5.0, label="AI Manager init")

    # ── LangSmith (non-blocking network init in background) ──────────────
    def _init_langsmith():
        from app.ai.langsmith_tracer import init_langsmith, langsmith_status
        init_langsmith()
        status = langsmith_status()
        if status["enabled"]:
            logger.info("LangSmith tracing ACTIVE", project=status["project"])
        else:
            logger.info("LangSmith tracing disabled")

    import threading as _t
    _t.Thread(target=_init_langsmith, daemon=True).start()
    # Fire-and-forget — never blocks server startup

    # ── Legacy Gemini (backward compat) ─────────────────────────────────
    def _init_legacy():
        try:
            from app.gemini.service import get_gemini_service
            get_gemini_service()
        except Exception:
            pass

    _t.Thread(target=_init_legacy, daemon=True).start()

    # ── SERVER IS READY ──────────────────────────────────────────────────
    bound_port = os.getenv("PORT", str(settings.PORT))
    logger.info("ResQAI backend ready", host="0.0.0.0", port=bound_port)

    yield  # <── Server is live and accepting requests here

    logger.info("ResQAI backend shutting down")


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="ResQAI API",
    description=(
        "AI-Powered Disaster Response & Resource Allocation Platform.\n\n"
        "**AI**: Mistral Large Latest → Gemini 1.5 Pro → Rule-based fallback\n"
        "**Observability**: LangSmith"
    ),
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(RequestLoggerMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health endpoints ──────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe — always returns 200 immediately."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe — checks service availability."""
    checks: dict = {}

    # Firebase / Demo
    if os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes"):
        checks["firebase"] = "demo_mode (in-memory)"
    else:
        try:
            import concurrent.futures
            from app.firebase.client import get_firestore_client
            with concurrent.futures.ThreadPoolExecutor() as ex:
                fut = ex.submit(lambda: get_firestore_client().collection("settings").document("system").get())
                fut.result(timeout=3)
            checks["firebase"] = "ok"
        except concurrent.futures.TimeoutError:
            checks["firebase"] = "timeout"
        except Exception as e:
            checks["firebase"] = f"error: {str(e)[:60]}"

    # Mistral
    try:
        from app.ai.mistral_service import get_mistral_service, _mistral_circuit
        svc = get_mistral_service()
        checks["mistral"] = "ok" if (svc._client and not _mistral_circuit.is_open) else "unavailable"
    except Exception:
        checks["mistral"] = "error"

    # Gemini fallback
    try:
        from app.ai.gemini_service import get_gemini_fallback_service
        checks["gemini_fallback"] = "ok" if get_gemini_fallback_service().is_available else "unavailable"
    except Exception:
        checks["gemini_fallback"] = "error"

    # LangSmith
    try:
        from app.ai.langsmith_tracer import langsmith_status
        ls = langsmith_status()
        checks["langsmith"] = "active" if ls["enabled"] else "disabled"
    except Exception:
        checks["langsmith"] = "unknown"

    return {
        "status": "ready",
        "checks": checks,
        "ai_pipeline": "mistral→gemini→rule-based",
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "ResQAI API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if not settings.is_production else "N/A",
    }


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    # Read PORT from environment — Render injects this at runtime
    port = int(os.getenv("PORT", str(settings.PORT)))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False,
    )
