"""
ResQAI – FastAPI Application Entry Point
Production-ready server with CORS, middleware, exception handlers, and health check.
Multi-LLM: Mistral (primary) → Gemini (fallback) with LangSmith tracing.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api import api_router
from app.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.firebase.client import initialize_firebase
from app.middleware.error_handler import register_exception_handlers
from app.middleware.request_logger import RequestLoggerMiddleware

# ── Setup logging first ────────────────────────────────────────────────────────
setup_logging()
logger = get_logger(__name__)
settings = get_settings()


# ── Lifespan: startup / shutdown ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""

    # ── STARTUP ──────────────────────────────────────────────────────────
    logger.info(
        "ResQAI backend starting",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    # Reset AI service singletons so they pick up fresh env keys on startup
    from app.ai.mistral_service import reset_mistral_service
    from app.ai.gemini_service import reset_gemini_fallback_service
    reset_mistral_service()
    reset_gemini_fallback_service()

    # 1. Firebase Admin SDK / Demo Mode
    import os as _os
    _demo = _os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    if _demo:
        logger.info("DEMO_MODE=true — in-memory store active, Firebase skipped")
        from app.demo.store import seed_demo_data
        seed_demo_data()
        logger.info("Demo data seeded — 3 incidents, 4 resources ready")
    else:
        try:
            initialize_firebase()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error("Firebase initialization failed", error=str(e))

    # 2. Mistral AI (Primary LLM)
    try:
        from app.ai.mistral_service import get_mistral_service
        mistral = get_mistral_service()
        if mistral.is_available:
            logger.info("Mistral AI (primary) initialized", model=settings.MISTRAL_MODEL)
        else:
            logger.warning("Mistral AI unavailable — will use Gemini directly")
    except Exception as e:
        logger.warning("Mistral initialization warning", error=str(e))

    # 3. Gemini AI (Fallback LLM)
    try:
        from app.ai.gemini_service import get_gemini_fallback_service
        gemini_fb = get_gemini_fallback_service()
        if gemini_fb.is_available:
            logger.info("Gemini AI (fallback) initialized", model=settings.GEMINI_MODEL)
        else:
            logger.warning("Gemini fallback unavailable — only rule-based fallback available")
    except Exception as e:
        logger.warning("Gemini fallback initialization warning", error=str(e))

    # 4. AI Manager (orchestrator)
    try:
        from app.ai.ai_manager import get_ai_manager
        get_ai_manager()
        logger.info("AI Manager initialized — Mistral→Gemini pipeline ready")
    except Exception as e:
        logger.warning("AI Manager initialization warning", error=str(e))

    # 5. LangSmith tracing
    try:
        from app.ai.langsmith_tracer import init_langsmith, langsmith_status
        init_langsmith()   # idempotent — safe to call again
        status = langsmith_status()
        if status["enabled"]:
            logger.info(
                "LangSmith tracing ACTIVE",
                project=status["project"],
                endpoint=status["endpoint"],
            )
        else:
            logger.info(
                "LangSmith tracing disabled",
                tracing_v2=status["tracing_v2"],
                has_key=status["has_api_key"],
                hint="Set LANGCHAIN_TRACING_V2=true and LANGSMITH_API_KEY to enable",
            )
    except Exception as e:
        logger.warning("LangSmith startup check failed", error=str(e))

    # 6. Legacy Gemini service (backward compat) — non-blocking
    import threading as _threading
    def _init_legacy_gemini():
        try:
            from app.gemini.service import get_gemini_service
            get_gemini_service()
        except Exception:
            pass
    _threading.Thread(target=_init_legacy_gemini, daemon=True).start()

    logger.info("ResQAI backend ready", host="0.0.0.0", port=settings.PORT)

    yield  # Application runs here

    # ── SHUTDOWN ─────────────────────────────────────────────────────────
    logger.info("ResQAI backend shutting down")


# ── Create FastAPI application ────────────────────────────────────────────────

app = FastAPI(
    title="ResQAI API",
    description=(
        "AI-Powered Disaster Response & Resource Allocation Platform.\n\n"
        "**AI Stack**: Mistral Large Latest (primary) → Gemini 1.5 Pro (fallback)\n"
        "**Observability**: LangSmith tracing on every AI call"
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

# ── Exception Handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


# ── Health Check Endpoints ───────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe — returns 200 if app is running."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness probe — checks all services.
    Reports: Firebase, Mistral (primary), Gemini (fallback), LangSmith.
    """
    checks: dict = {}

    # Firebase
    try:
        import concurrent.futures
        from app.firebase.client import get_firestore_client
        def _fb_check():
            db = get_firestore_client()
            db.collection("settings").document("system").get()
        with concurrent.futures.ThreadPoolExecutor() as ex:
            fut = ex.submit(_fb_check)
            fut.result(timeout=3)   # 3-second timeout
        checks["firebase"] = "ok"
    except concurrent.futures.TimeoutError:
        checks["firebase"] = "timeout (credentials may be missing)"
    except Exception as e:
        checks["firebase"] = f"error: {str(e)[:60]}"

    # Mistral (primary LLM)
    try:
        from app.ai.mistral_service import get_mistral_service, _mistral_circuit
        svc = get_mistral_service()
        if not svc._client:
            checks["mistral"] = "disabled (no API key)"
        elif _mistral_circuit.is_open:
            checks["mistral"] = "circuit_open"
        else:
            checks["mistral"] = "ok"
    except Exception as e:
        checks["mistral"] = f"error: {str(e)[:80]}"

    # Gemini (fallback LLM)
    try:
        from app.ai.gemini_service import get_gemini_fallback_service
        fb = get_gemini_fallback_service()
        checks["gemini_fallback"] = "ok" if fb.is_available else "disabled (no API key)"
    except Exception as e:
        checks["gemini_fallback"] = f"error: {str(e)[:80]}"

    # LangSmith
    try:
        from app.ai.langsmith_tracer import langsmith_status
        ls = langsmith_status()
        checks["langsmith"] = {
            "enabled": ls["enabled"],
            "project": ls["project"],
            "tracing_v2": ls["tracing_v2"],
            "has_api_key": ls["has_api_key"],
            "status": "ok" if ls["enabled"] else "disabled",
        }
    except Exception as e:
        checks["langsmith"] = {"status": "error", "detail": str(e)[:80]}

    # Overall health
    critical_checks = {k: v for k, v in checks.items()
                       if k in ("firebase",) and v != "ok"}
    status = "degraded" if critical_checks else "ready"

    return {
        "status": status,
        "checks": checks,
        "ai_pipeline": "mistral→gemini→rule-based",
    }


@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "ResQAI API",
        "version": settings.APP_VERSION,
        "ai": {
            "primary": "mistral-large-latest",
            "fallback": "gemini-1.5-pro",
            "observability": "langsmith",
        },
        "docs": "/docs" if not settings.is_production else "disabled in production",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=False,
    )
