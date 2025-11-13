# Railway Deployment - Better Free Tier Support

Railway supports background workers on the free tier! Let's deploy there instead.

## Quick Railway Deployment

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy to Railway:**
   ```bash
   railway login
   railway link
   railway up
   ```

3. **Add Services:**
   Railway will automatically detect and set up:
   - Web service (FastAPI)
   - PostgreSQL database
   - Redis service
   - Background workers (both webhook and upload)

## Free Tier Railway Benefits:
- ✅ Background workers supported
- ✅ PostgreSQL included
- ✅ Redis included  
- ✅ $5/month free credit
- ✅ No worker limitations

Would you like to try Railway instead? It's perfect for your dual-queue Celery setup!