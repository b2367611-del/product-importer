#!/bin/bash

# Development startup script for Product Importer

echo "🚀 Starting Product Importer Development Environment"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "Please update the .env file with your database and Redis configurations"
fi

# Check if database is accessible
echo "🗄️ Checking database connection..."
if ! python -c "
import os
from sqlalchemy import create_engine
from app.config import settings
try:
    engine = create_engine(settings.database_url)
    engine.connect()
    print('Database connection successful!')
except Exception as e:
    print(f'Database connection failed: {e}')
    print('Please make sure PostgreSQL is running and configured correctly')
    exit(1)
"; then
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Start Redis if not running (Linux/Mac)
if command -v redis-server > /dev/null; then
    if ! pgrep redis-server > /dev/null; then
        echo "🔴 Starting Redis server..."
        redis-server --daemonize yes
    else
        echo "✅ Redis is already running"
    fi
fi

echo "✅ Setup complete!"
echo ""
echo "🌟 Available commands:"
echo "  Start web server:    uvicorn app.main:app --reload"
echo "  Start Celery worker: celery -A app.celery worker --loglevel=info"
echo "  Run with Docker:     docker-compose up"
echo ""
echo "📋 Sample CSV file available: sample_products.csv"
echo "🌍 Access the app at: http://localhost:8000"
echo "📖 API docs at: http://localhost:8000/docs"