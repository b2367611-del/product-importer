# Product Importer - Complete Deployment Guide

## Prerequisites Installation

### 1. Install Git for Windows
1. Download Git from: https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart PowerShell/Command Prompt after installation
4. Verify installation: `git --version`

### 2. Install Heroku CLI
1. Download from: https://devcenter.heroku.com/articles/heroku-cli
2. Run the installer
3. Restart PowerShell after installation
4. Login to Heroku: `heroku login`

## Step-by-Step Deployment

### Phase 1: GitHub Repository Setup

1. **Initialize Git Repository:**
   ```powershell
   cd C:\Projects\Product_Importer
   git init
   git add .
   git commit -m "Initial commit: Product Importer with dual-queue webhook system"
   ```

2. **Create GitHub Repository:**
   - Go to https://github.com/new
   - Repository name: `product-importer`
   - Description: `FastAPI Product Import System with Webhook Integration`
   - Set to Public or Private as needed
   - Don't initialize with README (we already have one)
   - Click "Create repository"

3. **Connect and Push to GitHub:**
   ```powershell
   git remote add origin https://github.com/YOUR_USERNAME/product-importer.git
   git branch -M main
   git push -u origin main
   ```

### Phase 2: Heroku Deployment

#### Option A: Automated Deployment (Recommended)
Run the PowerShell script:
```powershell
.\deploy-heroku.ps1
```

#### Option B: Manual Deployment
1. **Create Heroku App:**
   ```powershell
   heroku create your-product-importer
   ```

2. **Add PostgreSQL and Redis:**
   ```powershell
   heroku addons:create heroku-postgresql:mini
   heroku addons:create heroku-redis:mini
   ```

3. **Set Environment Variables:**
   ```powershell
   heroku config:set SECRET_KEY="your-secret-key-here"
   heroku config:set ENVIRONMENT="production"
   ```

4. **Deploy Application:**
   ```powershell
   git push heroku main
   ```

5. **Scale Workers:**
   ```powershell
   heroku ps:scale web=1 webhook_worker=1 upload_worker=1
   ```

6. **Initialize Database:**
   ```powershell
   heroku run python -c "from app.database import init_db; init_db()"
   ```

### Phase 3: Post-Deployment Configuration

1. **Get Application URL:**
   ```powershell
   heroku open
   ```

2. **View Logs:**
   ```powershell
   heroku logs --tail
   ```

3. **Test Webhook System:**
   - Go to your app URL
   - Navigate to webhook configuration
   - Set up test webhooks using webhook.site
   - Test all four event types (created, updated, deleted, bulk_imported)

## System Architecture

### Dual-Queue System
- **webhook_queue**: Fast webhook notifications (1 worker)
- **upload_queue**: Heavy file processing (1 worker)

### Process Structure
- **web**: FastAPI application server
- **webhook_worker**: Handles webhook notifications
- **upload_worker**: Processes large file imports

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Heroku |
| `REDIS_URL` | Redis connection string | Auto-set by Heroku |
| `SECRET_KEY` | FastAPI secret key | Must be set |
| `ENVIRONMENT` | Deployment environment | production |

## Monitoring and Maintenance

### Check Application Health
```powershell
heroku ps
heroku logs --tail
```

### Scale Workers
```powershell
heroku ps:scale webhook_worker=2  # Scale webhook workers
heroku ps:scale upload_worker=1   # Keep upload worker at 1
```

### Database Management
```powershell
heroku pg:info                    # Database info
heroku pg:psql                    # Connect to database
```

### Redis Management
```powershell
heroku redis:info                 # Redis info
heroku redis:cli                  # Connect to Redis
```

## Troubleshooting

### Common Issues

1. **Workers Not Starting:**
   ```powershell
   heroku logs --tail --dyno=webhook_worker
   heroku restart webhook_worker
   ```

2. **Database Connection Issues:**
   ```powershell
   heroku config:get DATABASE_URL
   heroku pg:reset DATABASE_URL --confirm your-app-name
   ```

3. **Webhook Not Triggering:**
   - Check worker logs: `heroku logs --tail --dyno=webhook_worker`
   - Verify Redis connection: `heroku redis:info`
   - Test webhook endpoints manually

### Performance Optimization

- Monitor dyno usage: `heroku ps`
- Scale workers based on load: `heroku ps:scale webhook_worker=2`
- Upgrade database if needed: `heroku addons:upgrade DATABASE_URL:basic`

## Support

For issues or questions:
1. Check logs: `heroku logs --tail`
2. Monitor workers: `heroku ps`
3. Review webhook configuration in the web interface
4. Test with webhook.site for debugging

## Success Criteria

✅ GitHub repository created and code pushed
✅ Heroku app deployed with all addons
✅ All three processes running (web, webhook_worker, upload_worker)
✅ Database initialized and accessible
✅ Webhook system responding to all event types
✅ Large file uploads processing without blocking webhooks