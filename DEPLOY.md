# Product Importer Deployment Guide

## Quick Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Manual Deployment Steps

### 1. Prepare for GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Product Importer with webhook system"

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/Product_Importer.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to Heroku

#### Option A: Using Heroku CLI

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Add Redis addon
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set DEBUG=false
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main

# Scale workers
heroku ps:scale web=1 webhook_worker=1 upload_worker=1

# Run database migrations
heroku run alembic upgrade head
```

#### Option B: Using GitHub Integration

1. Go to [Heroku Dashboard](https://dashboard.heroku.com)
2. Click "New" → "Create new app"
3. Connect to your GitHub repository
4. Enable automatic deploys
5. Add the required addons and config vars as shown above

### 3. Required Heroku Addons

- **Heroku Postgres** (Mini plan: $7/month)
- **Heroku Redis** (Mini plan: $3/month)

### 4. Environment Variables

Set these in Heroku config vars:

```
DATABASE_URL=postgres://... (automatically set by Heroku Postgres)
REDIS_URL=redis://... (automatically set by Heroku Redis)
SECRET_KEY=your-secret-key
DEBUG=false
ENVIRONMENT=production
```

### 5. Worker Configuration

The app uses 3 processes:

- **web**: FastAPI server
- **webhook_worker**: Handles webhook tasks (fast)
- **upload_worker**: Handles file uploads (can be slow)

### 6. Testing the Deployment

After deployment, test:

1. Visit your app URL
2. Create a webhook pointing to webhook.site
3. Test product creation/update/deletion
4. Test CSV file upload
5. Verify webhooks are sent correctly

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start webhook worker (Terminal 2)
celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h

# Start upload worker (Terminal 3)
celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h
```

## Architecture

- **FastAPI**: Web server and API
- **PostgreSQL**: Database with JSON support
- **Redis**: Message broker for Celery
- **Celery**: Background task processing with separate queues
- **Webhook System**: Real-time notifications for CRUD operations

## Features

- ✅ Large CSV file imports (100MB+)
- ✅ Real-time webhook notifications
- ✅ Separate queues for uploads and webhooks
- ✅ PostgreSQL with JSON support
- ✅ Responsive web interface
- ✅ Background task processing
- ✅ Production-ready deployment