#!/bin/bash
set -e

echo "=== Starting Django Blog API Container ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "PORT: ${PORT:-8080}"

# Use PORT environment variable (App Runner sets this to 8080)
PORT=${PORT:-8080}

# Run migrations BEFORE starting Gunicorn to avoid race conditions
echo "Running database migrations..."
python manage.py migrate --noinput || echo "Warning: Migrations failed, continuing..."

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn --config gunicorn.conf.py leather_api.wsgi:application
