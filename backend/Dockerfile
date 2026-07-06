# ═══════════════════════════════════════════════════════════════════════════════
# ResQAI Backend — Production Dockerfile
# Render / Cloud Run / Docker compatible.
#
# KEY DESIGN DECISIONS:
#   - PORT is read from $PORT env var at runtime (Render injects it)
#   - Uses Python 3.11-slim (3.12 has pygeohash build issues on some platforms)
#   - Single stage for simplicity and faster Render build
#   - Non-root user for security
#   - EXPOSE is documentation only — actual port comes from $PORT
# ═══════════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

# ── System deps ───────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── App directory ─────────────────────────────────────────────────────────────
WORKDIR /app

# ── Python env ────────────────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# ── Install dependencies first (cached layer) ─────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
COPY . .

# ── Non-root user ─────────────────────────────────────────────────────────────
RUN groupadd -g 1001 resqai && \
    useradd -u 1001 -g resqai -s /bin/sh -m resqai && \
    chown -R resqai:resqai /app

USER resqai

# ── Default port (Render overrides this with $PORT env var) ───────────────────
ENV PORT=10000

# EXPOSE is documentation only — Render uses $PORT
EXPOSE 10000

# ── Health check ──────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# ── Start command ─────────────────────────────────────────────────────────────
# Uses shell form so $PORT is expanded at runtime from Render's environment
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level warning --no-access-log
