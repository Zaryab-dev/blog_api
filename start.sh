#!/bin/bash
# Quick start script

echo "🚀 Starting Django Blog API..."

# Activate venv
source venv/bin/activate

# Run migrations
python3 manage.py migrate

# Start server
python3 manage.py runserver

echo "✅ Server running at http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/v1/docs/"
