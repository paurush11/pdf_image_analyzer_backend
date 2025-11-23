# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    # set these via env/.env in dev; ECS will override in prod
    DJANGO_SETTINGS_MODULE=config.settings \
    PYTHONPATH=/app

# System deps (Postgres client libs for psycopg2, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for better security
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Separate layer for deps
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy source
COPY . .

# Switch to non-root
USER appuser

# Default entrypoint = web (workers/beat/flower override in docker-compose or ECS)
EXPOSE 8000
# Health endpoint should exist in Django (e.g., /healthz)
HEALTHCHECK --interval=30s --timeout=5s --retries=5 CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1

CMD ["gunicorn","config.asgi:application","-k","uvicorn.workers.UvicornWorker","-w","4","-b","0.0.0.0:8000"]
