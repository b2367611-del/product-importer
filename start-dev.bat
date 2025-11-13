@echo off
REM Development startup script for Product Importer (Windows)

echo 🚀 Starting Product Importer Development Environment

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo Please update the .env file with your database and Redis configurations
)

REM Run database migrations
echo 🔄 Running database migrations...
alembic upgrade head

echo ✅ Setup complete!
echo.
echo 🌟 Available commands:
echo   Start web server:    uvicorn app.main:app --reload
echo   Start Celery worker: celery -A app.celery worker --loglevel=info
echo   Run with Docker:     docker-compose up
echo.
echo 📋 Sample CSV file available: sample_products.csv
echo 🌍 Access the app at: http://localhost:8000
echo 📖 API docs at: http://localhost:8000/docs

pause