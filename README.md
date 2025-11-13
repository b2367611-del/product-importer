# Product Importer

A FastAPI-based web application for importing product data from CSV files with webhook integration and background processing capabilities.

## Features

- **CSV File Upload**: Import product data from CSV files
- **Webhook Integration**: Real-time notifications for product events (create, update, delete, bulk import)
- **Background Processing**: Asynchronous task processing using Celery
- **Dual Queue System**: Separate queues for webhook notifications and file processing
- **Database Management**: PostgreSQL with SQLAlchemy ORM
- **Web Interface**: Clean, responsive web interface for file uploads and webhook management
- **Real-time Monitoring**: Track import progress and webhook delivery status

## Quick Start Guide

### Prerequisites
- Python 3.11+ installed
- PostgreSQL 17+ installed and running
- Redis 7+ installed and running

### 1. Download and Setup

```bash
# Clone the repository
git clone https://github.com/b2367611-del/product-importer.git
cd product-importer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```sql
-- Create PostgreSQL database (run in psql or pgAdmin)
CREATE DATABASE product_importer;
```

### 3. Environment Configuration

Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/product_importer
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here-change-this
ENVIRONMENT=development
```

### 4. Initialize Database

```bash
# Run database migrations
alembic upgrade head
```

### 5. Start Services

You'll need 4 terminals/command prompts:

**Terminal 1 - Start Redis:**
```bash
redis-server
```

**Terminal 2 - Start Webhook Worker:**
```bash
celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h
```

**Terminal 3 - Start Upload Worker:**
```bash
celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h
```

**Terminal 4 - Start Web Application:**
```bash
uvicorn app.main:app --reload
```

### 6. Access the Application

Open your browser and go to: `http://localhost:8000`

## How to Use

### Upload CSV Files
1. Go to the main page
2. Click "Choose File" and select your CSV file
3. Click "Upload CSV" to process
4. Monitor progress in real-time

### Set Up Webhooks
1. Navigate to webhook configuration
2. Add webhook URLs for different events:
   - Product Created
   - Product Updated
   - Product Deleted
   - Bulk Import Completed
3. Use https://webhook.site to test webhooks
4. Click "Play" button to test each webhook

### CSV File Format
Your CSV should have these columns:
```csv
name,description,price,category,sku
Product 1,Description 1,29.99,Electronics,SKU001
Product 2,Description 2,49.99,Books,SKU002
```

## Architecture

### Core Components
- **FastAPI**: Modern web framework for APIs
- **PostgreSQL**: Database for product storage
- **Redis**: Message broker for task queues
- **Celery**: Background task processing
- **SQLAlchemy**: Database ORM

### Dual Queue System
- **webhook_queue**: Fast webhook notifications
- **upload_queue**: Heavy file processing

This ensures webhooks stay fast even during large file uploads.

## Troubleshooting

### Common Issues

**"Database connection failed"**
- Make sure PostgreSQL is running
- Check your DATABASE_URL in .env file
- Verify database `product_importer` exists

**"Redis connection failed"**
- Make sure Redis server is running
- Check REDIS_URL in .env file
- Try: `redis-cli ping` (should return PONG)

**"Workers not processing tasks"**
- Make sure both Celery workers are running
- Check worker logs for errors
- Restart workers if needed

**"Webhooks not firing"**
- Verify webhook URLs are correct
- Check webhook workers are running
- Test with webhook.site first

### Reset Everything
If you need to start fresh:
```bash
# Stop all services (Ctrl+C in each terminal)

# Reset database
DROP DATABASE product_importer;
CREATE DATABASE product_importer;

# Re-run migrations
alembic upgrade head

# Restart all services
```

## Project Structure
```
product-importer/
├── app/
│   ├── api/v1/          # API routes
│   ├── models/          # Database models
│   ├── tasks/           # Background tasks
│   ├── database.py      # Database config
│   ├── celery.py        # Celery config
│   └── main.py          # FastAPI app
├── static/              # CSS, JS files
├── templates/           # HTML templates
├── uploads/             # File uploads
├── requirements.txt     # Python dependencies
├── alembic/            # Database migrations
└── README.md
```

## Development Notes

### Adding New Features
1. Models go in `app/models/`
2. API routes go in `app/api/v1/`
3. Background tasks go in `app/tasks/`
4. Run migrations: `alembic revision --autogenerate -m "description"`

### Testing Webhooks
1. Go to https://webhook.site
2. Copy the unique URL
3. Add to webhook configuration
4. Create/update/delete products to see webhooks

## Support

Having issues? Check:
1. All 4 services are running (Redis, 2 workers, web app)
2. Database connection is working
3. .env file has correct settings
4. Check terminal logs for error messages

## Technology Stack

- **Backend**: FastAPI 0.104.1
- **Database**: PostgreSQL 17 with JSON support
- **Message Broker**: Redis 7
- **Task Queue**: Celery 5.3.4
- **ORM**: SQLAlchemy 2.0.23
- **Frontend**: HTML/CSS/JavaScript
- **File Processing**: Pandas

## License

MIT License - see LICENSE file for details.