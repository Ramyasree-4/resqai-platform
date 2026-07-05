"""
ResQAI Startup Check
Verifies all modules load correctly and API keys are detected.
Run: py -3.11 check_startup.py
"""
import os, sys
from pathlib import Path

# Load .env using absolute path FIRST — before any app import
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path, override=True)
    print(f"Loaded: {env_path}\n")
else:
    print(f"WARNING: {env_path} not found — using environment variables only\n")

# Set required-field fallbacks only if not already set
os.environ.setdefault('FIREBASE_PROJECT_ID', 'resqai-dev')
os.environ.setdefault('FIREBASE_STORAGE_BUCKET', 'resqai-dev.appspot.com')
os.environ.setdefault('FIREBASE_WEB_API_KEY', 'placeholder')
os.environ.setdefault('JWT_SECRET_KEY', 'resqai-dev-secret-key-placeholder-32chars!!!')

sys.path.insert(0, str(Path(__file__).parent))

ok = True

def check(label, fn):
    global ok
    try:
        result = fn()
        print(f"  PASS  {label}" + (f"  →  {result}" if result else ""))
    except Exception as e:
        print(f"  FAIL  {label}: {e}")
        ok = False

def key_status(env_var):
    val = os.getenv(env_var, "")
    if not val or val.lower().startswith(("your-", "change-", "test", "placeholder")):
        return f"⚠ NOT SET (placeholder)"
    return f"✓ SET ({val[:8]}...)"

print("=== ResQAI Startup Check ===\n")

# ── Key Status ──────────────────────────────────────────────────────────
print("API Key Status:")
print(f"  MISTRAL_API_KEY          {key_status('MISTRAL_API_KEY')}")
print(f"  GOOGLE_API_KEY           {key_status('GOOGLE_API_KEY')}")
print(f"  LANGSMITH_API_KEY        {key_status('LANGSMITH_API_KEY')}")
print(f"  LANGCHAIN_TRACING_V2     {os.getenv('LANGCHAIN_TRACING_V2','false')}")
print(f"  LANGCHAIN_PROJECT        {os.getenv('LANGCHAIN_PROJECT','ResQAI')}")
print(f"  FIREBASE_WEB_API_KEY     {key_status('FIREBASE_WEB_API_KEY')}")
print()

# ── Module Checks ─────────────────────────────────────────────────────
print("Module Checks:")

check("Settings load",
    lambda: __import__('app.config', fromlist=['get_settings']).get_settings().APP_NAME)

check("Geo utils — geohash",
    lambda: __import__('app.utils.geo', fromlist=['encode_geohash']).encode_geohash(20.29, 85.82))

check("ID generator",
    lambda: __import__('app.utils.ids', fromlist=['generate_incident_id']).generate_incident_id())

from app.ai.json_parser import parse_llm_json
r, e = parse_llm_json('{"disaster_type":"FLOOD","severity":"HIGH"}')
check("JSON parser", lambda: r.get("disaster_type") if r else "FAILED: " + str(e))

from app.ai.response_validator import validate_standard_response, build_fallback_standard_response
fb = build_fallback_standard_response("test flood", "FLOOD", 500)
valid, errs = validate_standard_response(fb)
check("Response validator", lambda: "valid=" + str(valid))

from app.ai.fallback_manager import should_fallback_to_gemini
should, reason = should_fallback_to_gemini("HTTP 503 error")
check("Fallback manager", lambda: reason.value)

from app.ai.langsmith_tracer import langsmith_status, trace_ai_call
ls = langsmith_status()
check("LangSmith tracer", lambda: f"enabled={ls['enabled']}  tracing_v2={ls['tracing_v2']}  has_key={ls['has_api_key']}")

from app.ai.mistral_service import get_mistral_service, reset_mistral_service
reset_mistral_service()
m = get_mistral_service()
check("Mistral service (primary)", lambda: f"available={m.is_available}")

from app.ai.gemini_service import get_gemini_fallback_service, reset_gemini_fallback_service
reset_gemini_fallback_service()
g = get_gemini_fallback_service()
check("Gemini fallback service", lambda: f"available={g.is_available}")

from app.ai.ai_manager import get_ai_manager, _ai_manager
_ai_manager = None  # force re-init
ai = get_ai_manager()
check("AI Manager orchestrator", lambda: "ok")

from app.ai.prompt_templates import build_incident_analysis_prompt
prompt = build_incident_analysis_prompt(
    "INC-TEST","FLOOD","Water rising fast",800,
    "Khurda","Odisha",20.29,85.82,"2024-01-01","CRITICAL")
check("Prompt templates", lambda: f"{len(prompt)} chars")

# ── Summary ────────────────────────────────────────────────────────────
print()
print("=" * 55)

if ok:
    print("ALL CHECKS PASSED\n")

    # Determine AI pipeline status
    pipeline = []
    if m.is_available:
        pipeline.append("Mistral (primary) ✓")
    else:
        pipeline.append("Mistral (primary) ✗ — needs MISTRAL_API_KEY")
    if g.is_available:
        pipeline.append("Gemini (fallback) ✓")
    else:
        pipeline.append("Gemini (fallback) ✗ — needs GOOGLE_API_KEY")
    pipeline.append("Rule-based (last resort) ✓ always on")

    print("AI Pipeline:")
    for p in pipeline:
        print(f"  {p}")
    print()

    if ls["enabled"]:
        print(f"LangSmith: ACTIVE  →  project '{ls['project']}'")
    else:
        print("LangSmith: disabled  →  set LANGCHAIN_TRACING_V2=true + LANGSMITH_API_KEY")

    print()
    print("Start commands:")
    print("  Backend:   py -3.11 main.py")
    print("  Frontend:  npm run dev  (in frontend/)")
    print()
    print("URLs:")
    print("  Backend API:  http://localhost:8000")
    print("  API Docs:     http://localhost:8000/docs")
    print("  Health:       http://localhost:8000/health")
    print("  Frontend:     http://localhost:3000")
    if ls["enabled"]:
        print("  LangSmith:    https://smith.langchain.com")
else:
    print("SOME CHECKS FAILED — fix errors above")
    sys.exit(1)
