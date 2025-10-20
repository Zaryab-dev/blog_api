#!/bin/bash
set -e

echo "=== Starting Django Blog API Container ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"

# Use PORT environment variable (App Runner sets this to 8080)
PORT=${PORT:-8080}

# Start Gunicorn IMMEDIATELY to pass health checks
echo "Starting Gunicorn on 0.0.0.0:$PORT..."

# Run migrations in background after Gunicorn starts
(
    sleep 2
    echo "[Background] Running migrations..."
    python manage.py migrate --noinput 2>&1 | sed 's/^/[Background] /'
    echo "[Background] Setup complete!"
) &
exec gunicorn --bind 0.0.0.0:$PORT \
    --workers 3 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    leather_api.wsgi:application
