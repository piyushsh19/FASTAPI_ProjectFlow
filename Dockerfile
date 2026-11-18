
# ==================================================
# Stage 1: Builder
# ==================================================

FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1

WORKDIR /build

# Copy production dependencies only
COPY requirements.txt .

# Build wheels for all production dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip wheel \
        --no-cache-dir \
        --wheel-dir /wheels \
        -r requirements.txt


# ==================================================
# Stage 2: Production Runtime
# ==================================================

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy dependency wheels from builder
COPY --from=builder /wheels /wheels
COPY requirements.txt .

# Install dependencies without accessing the internet
RUN python -m pip install \
        --no-cache-dir \
        --no-index \
        --find-links=/wheels \
        -r requirements.txt \
    && rm -rf /wheels

# Copy application files
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create dedicated non-root user
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Container health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=3)" || exit 1

# Start FastAPI
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
