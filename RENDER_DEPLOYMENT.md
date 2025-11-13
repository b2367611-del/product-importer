# Product Importer - Render Deployment Guide

## 🚀 Why Render is Perfect for Your App

✅ **Native support for background workers** (Celery)  
✅ **Built-in PostgreSQL** database  
✅ **Built-in Redis** service  
✅ **Multiple services** in one project  
✅ **Auto-scaling** and monitoring  
✅ **Free tier available** for testing  

## 📋 Prerequisites

1. **GitHub Repository**: Already done ✅
2. **Render Account**: Sign up at https://render.com

## 🎯 Deployment Methods

### Method 1: Automatic Deployment (Recommended)

1. **Connect GitHub to Render:**
   - Go to https://render.com/dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select repository: `product-importer`
   - Render will automatically detect `render.yaml`

2. **Review Configuration:**
   - Web service: FastAPI application
   - Webhook worker: Dedicated webhook processing
   - Upload worker: Large file processing
   - PostgreSQL database: Persistent storage
   - Redis: Task queue and caching

3. **Deploy:**
   - Click "Apply" to create all services
   - Wait for deployment (5-10 minutes)

### Method 2: Manual Service Creation

If automatic deployment doesn't work:

1. **Create Database:**
   - New → PostgreSQL
   - Name: `product-importer-db`
   - Plan: Starter (Free)

2. **Create Redis:**
   - New → Redis
   - Name: `product-importer-redis`
   - Plan: Starter (Free)

3. **Create Web Service:**
   - New → Web Service
   - Connect GitHub repo: `product-importer`
   - Name: `product-importer-web`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Create Workers:**
   - New → Background Worker (webhook-worker)
   - Start Command: `celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h`
   - New → Background Worker (upload-worker)
   - Start Command: `celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h`

## 🔧 Environment Variables

Render will automatically set:
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection  
- `SECRET_KEY`: Auto-generated secure key
- `PORT`: Service port (auto-assigned)

## 📊 Service Overview

| Service | Type | Purpose | Resource |
|---------|------|---------|----------|
| Web | Web Service | FastAPI app | 512MB RAM |
| Webhook Worker | Background Worker | Fast webhook processing | 512MB RAM |
| Upload Worker | Background Worker | Large file uploads | 512MB RAM |
| Database | PostgreSQL | Data storage | 1GB Storage |
| Redis | Redis | Task queues | 25MB Memory |

## 🎉 Post-Deployment Steps

1. **Get Your App URL:**
   - Check the web service dashboard
   - URL format: `https://product-importer-web.onrender.com`

2. **Initialize Database:**
   - Go to web service → Shell
   - Run: `python -c "from app.database import init_db; init_db()"`

3. **Test Webhook System:**
   - Navigate to your app URL
   - Test all webhook event types
   - Verify workers are processing tasks

## 🔍 Monitoring

- **Logs**: Available in each service dashboard
- **Metrics**: CPU, memory, and request analytics
- **Health Checks**: Automatic service monitoring
- **Alerts**: Email notifications for issues

## 💰 Pricing

**Free Tier Limits:**
- Web Service: 750 hours/month
- Background Workers: 750 hours/month each
- PostgreSQL: 1GB storage, 1 month retention
- Redis: 25MB memory

**Paid Plans:**
- Start at $7/month per service
- More CPU, memory, and features

## 🔧 Troubleshooting

### Workers Not Starting
```bash
# Check worker logs in Render dashboard
# Verify Redis connection
# Ensure queue names match
```

### Database Connection Issues
```bash
# Check DATABASE_URL environment variable
# Verify PostgreSQL service is running
# Test connection from web service shell
```

### Webhook Not Triggering
```bash
# Check webhook worker logs
# Verify Redis task queue
# Test webhook endpoints manually
```

## 🚀 Quick Start Commands

1. **Sign up**: https://render.com
2. **Connect GitHub**: Link your repository
3. **Deploy Blueprint**: Use `render.yaml` for automatic setup
4. **Monitor**: Check service dashboards
5. **Test**: Verify webhook functionality

## ✅ Success Criteria

- [ ] All 4 services deployed and running
- [ ] Database initialized with tables
- [ ] Webhook workers processing tasks
- [ ] Upload worker handling large files
- [ ] Web interface accessible
- [ ] All webhook event types working

**Your dual-queue webhook system will work perfectly on Render!**