#!/bin/bash
# Installation script for Bobager

set -e  # Exit on error

echo "🚀 Installing Bobager..."
echo ""

# Check Python version
echo "Checking Python version..."
python --version

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Verify installation
echo ""
echo "Verifying installation..."
pip check

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env: cp .env.example .env"
echo "2. Edit .env with your Slack API tokens: nano .env"
echo "3. Run the server: python -m uvicorn app.main:app --reload"
echo ""
