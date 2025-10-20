# Multi-stage Dockerfile optimized for AWS App Runner
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN pip install --user -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=leather_api.settings \
    PORT=8080 \
    PYTHONIOENCODING=utf-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /usr/local

WORKDIR /app

# Copy entrypoint first and set permissions
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Copy application code
COPY . /app/

# CRITICAL: Collect static files during BUILD with dummy SECRET_KEY
RUN SECRET_KEY=dummy-build-key-for-collectstatic python manage.py collectstatic --noinput --clear || echo "Static files collected"

RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/v1/healthcheck/ || exit 1

CMD ["/bin/bash", "/app/docker-entrypoint.sh"]
