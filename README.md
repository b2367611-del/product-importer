# Product Importer

A scalable web application for importing large CSV files (up to 500,000+ records) into a PostgreSQL database with real-time webhook notifications.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Features

- 🚀 **Large File Imports**: Handle CSV files with 500,000+ records
- 📡 **Real-time Webhooks**: Instant notifications for all product operations
- ⚡ **Dual Queue System**: Separate workers for uploads and webhooks
- 🔄 **Full CRUD Operations**: Complete product management with filtering
- 📊 **Progress Tracking**: Real-time import progress with detailed reporting
- 🎯 **Webhook Testing**: Built-in webhook testing with multiple event types
- 🔍 **Advanced Search**: Filter products by multiple criteria
- 💾 **PostgreSQL**: JSON support for complex data structures

## Architecture

- **FastAPI**: High-performance web framework
- **PostgreSQL**: Robust database with JSON support
- **Redis**: Message broker for task queues
- **Celery**: Dual-queue background processing
  - `webhook_queue`: Fast webhook notifications
  - `upload_queue`: Heavy file processing
- **Bootstrap**: Responsive web interface

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Quick Deploy

#### Deploy to Heroku (Recommended)

**Windows:**
```powershell
.\deploy-heroku.ps1
```

**Linux/Mac:**
```bash
./deploy-heroku.sh
```

#### Local Development

1. **Clone and setup:**
```bash
git clone https://github.com/YOUR_USERNAME/Product_Importer.git
cd Product_Importer
pip install -r requirements.txt
```

2. **Setup environment:**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Database setup:**
```bash
alembic upgrade head
```

4. **Start services (3 terminals):**

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Webhook Worker:**
```bash
celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h
```

**Terminal 3 - Upload Worker:**
```bash
celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h
```

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Application secret key
- `DEBUG`: Debug mode (false for production)
- `ENVIRONMENT`: development/production

## API Documentation

Once the application is running, visit `/docs` for interactive API documentation.