# Product Importer Startup Guide

## Services Required

### 1. Redis/Memurai (Message Broker)
- **Status**: Should be running as Windows service
- **Check**: `Get-Service -Name "*memurai*"`
- **Port**: 6379

### 2. Celery Worker (Background Tasks)
- **Purpose**: Processes CSV imports and webhook tasks
- **Command**: `python -m celery -A app.celery worker --loglevel=info --pool=solo`
- **Script**: Run `start_celery.bat`

### 3. FastAPI Server (Web Application)
- **Purpose**: Web interface and API endpoints
- **Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Script**: Run `start_server.bat`
- **URL**: http://localhost:8000

## Quick Start Instructions

### Option 1: Using Batch Files (Recommended)
1. Double-click `start_celery.bat` (keep this window open)
2. Double-click `start_server.bat` (keep this window open)
3. Open browser to http://localhost:8000

### Option 2: Using PowerShell
1. **Terminal 1 - Celery Worker**:
   ```powershell
   cd C:\Projects\Product_Importer
   & .\.venv\Scripts\Activate.ps1
   python -m celery -A app.celery worker --loglevel=info --pool=solo
   ```

2. **Terminal 2 - FastAPI Server**:
   ```powershell
   cd C:\Projects\Product_Importer
   & .\.venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Verification Steps

1. **Check Redis**: `Test-NetConnection localhost -Port 6379`
2. **Check Celery**: Look for "celery@DESKTOP ready" message
3. **Check FastAPI**: Look for "Uvicorn running on http://0.0.0.0:8000"
4. **Test Application**: Visit http://localhost:8000

## Troubleshooting

- **Redis not running**: Start Memurai service
- **Database errors**: Ensure PostgreSQL is running
- **Task errors**: Restart Celery worker
- **Port conflicts**: Change port in start_server.bat

## Features Available

- ✅ CSV File Upload (up to 100MB)
- ✅ Real-time Progress Tracking
- ✅ Product Management (CRUD)
- ✅ Webhook Configuration
- ✅ Import Job History
- ✅ Bulk Operations