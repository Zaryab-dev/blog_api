#!/bin/bash
# Fix dependencies installation

echo "🔧 Fixing dependencies..."

# Activate venv
source venv/bin/activate

# Upgrade pip
pip3 install --upgrade pip

# Install all requirements
pip3 install -r requirements.txt

echo "✅ Dependencies installed!"
echo ""
echo "Now run:"
echo "  source venv/bin/activate"
echo "  python3 manage.py migrate"
