# Railway Deployment Guide - Complete Setup

## 🚀 Why Railway is Perfect for Your App

✅ **Background Workers Supported** on free tier  
✅ **$5/month free credit** (enough for development)  
✅ **Auto-detects services** from your code  
✅ **Built-in PostgreSQL & Redis**  
✅ **Zero configuration needed**  
✅ **Perfect for Celery workers**  

## 📋 Quick Deployment Steps

### 1. Install Railway CLI
```bash
# Using npm (if you have Node.js)
npm install -g @railway/cli

# OR using PowerShell (Windows)
iwr https://railway.app/install.ps1 | iex
```

### 2. Deploy Your App
```bash
# Login to Railway
railway login

# Link your GitHub repo (optional but recommended)
railway link

# Deploy your application
railway up
```

### 3. Add Database Services
Railway will automatically detect your app needs:
- **PostgreSQL** (for your database)
- **Redis** (for Celery task queues)

## 🔧 What Railway Auto-Detects

From your code, Railway will automatically:
1. **Web Service**: Detect FastAPI app from `app/main.py`
2. **Worker Services**: Detect Celery workers from `Procfile` or requirements
3. **Database**: Add PostgreSQL when it sees `psycopg2-binary`
4. **Redis**: Add Redis when it sees `celery` and `redis`

## 📊 Services That Will Be Created

| Service | Purpose | Auto-Detected |
|---------|---------|---------------|
| 🌐 **Web** | FastAPI application | ✅ From main.py |
| 🔄 **Webhook Worker** | Fast webhook processing | ✅ From Celery config |
| 📁 **Upload Worker** | Large file handling | ✅ From Celery config |
| 🗄️ **PostgreSQL** | Database | ✅ From requirements.txt |
| 🔴 **Redis** | Task queues | ✅ From requirements.txt |

## 💰 Railway Free Tier

- **$5/month free credit**
- **All services supported** (including workers!)
- **Automatic scaling**
- **Built-in monitoring**
- **Custom domains**

## 🎯 Alternative: One-Click Deploy

Visit: https://railway.app/new and connect your GitHub repository directly!

## 🔧 Manual Service Setup (If Needed)

If auto-detection doesn't work perfectly:

1. **Web Service:**
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

2. **Webhook Worker:**
   - Start Command: `celery -A app.celery worker --loglevel=info --pool=solo -Q webhook_queue -n webhook_worker@%h`

3. **Upload Worker:**
   - Start Command: `celery -A app.celery worker --loglevel=info --pool=solo -Q upload_queue -n upload_worker@%h`

## 🚀 Deployment Commands

```bash
# Method 1: Direct deployment
railway up

# Method 2: GitHub integration
railway link
railway up --detach

# Method 3: One-click from web
# Go to railway.app/new and select your repo
```

## 📱 After Deployment

1. **Get Your URL**: Railway provides a custom URL automatically
2. **Environment Variables**: Automatically set for database connections
3. **Monitor Services**: Built-in dashboard for all services
4. **View Logs**: Real-time logs for debugging

## ✅ Success Indicators

- [ ] Web service deployed and accessible
- [ ] PostgreSQL database connected
- [ ] Redis service running
- [ ] Webhook worker processing tasks
- [ ] Upload worker handling files
- [ ] All webhook event types working

## 🔍 Troubleshooting

**If services don't auto-deploy:**
1. Check the Railway dashboard
2. Add services manually:
   - Add PostgreSQL plugin
   - Add Redis plugin
   - Configure worker start commands

**Environment Variables:**
Railway automatically sets:
- `DATABASE_URL`
- `REDIS_URL`
- `PORT`

## 🎉 Advantages Over Other Platforms

| Feature | Railway | Render Free | Heroku |
|---------|---------|-------------|---------|
| Background Workers | ✅ Yes | ❌ No | ✅ Yes ($) |
| Free Database | ✅ Yes | ✅ 90 days | ❌ No |
| Free Redis | ✅ Yes | ✅ 25MB | ❌ No |
| Easy Setup | ✅ One command | ⚠️ Complex | ⚠️ Complex |
| Worker Support | ✅ Free tier | ❌ Paid only | ✅ Paid only |

**Railway is the perfect fit for your dual-queue webhook system!** 🚀