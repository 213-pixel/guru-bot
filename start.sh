#!/bin/bash

echo "🚀 Starting Guru Assistant Bot..."

# Install dependencies
pip install -r requirements.txt

# Set webhook
echo "Setting webhook..."
python set_webhook.py

# Start the app
echo "Starting FastAPI server..."
uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}