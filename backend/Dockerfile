# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a prefix directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Production Runner ────────────────────────────────────────────────
FROM python:3.12-slim AS runner

WORKDIR /app

# Security: non-root user
RUN groupadd -g 1001 resqai && \
    useradd -u 1001 -g resqai -s /bin/sh -m resqai

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY --chown=resqai:resqai . .

# Switch to non-root
USER resqai

# Cloud Run uses PORT env var
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--workers", "1", \
     "--log-level", "warning", \
     "--no-access-log"]
