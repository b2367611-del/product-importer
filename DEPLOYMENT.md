# Deployment scripts for Product Importer

## Local Development with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM available for containers

### Quick Start
1. Clone the repository
2. Copy environment file: `cp .env.example .env`
3. Update `.env` with your settings
4. Start services: `docker-compose up -d`
5. Access the application at: http://localhost:8000

### Services
- **Web Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Celery Flower (monitoring)**: http://localhost:5555
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Useful Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web
docker-compose logs -f celery-worker

# Run database migrations
docker-compose exec web alembic upgrade head

# Access database
docker-compose exec postgres psql -U postgres -d product_importer

# Stop all services
docker-compose down

# Stop and remove volumes (careful - this deletes data)
docker-compose down -v
```

## Production Deployment

### Heroku Deployment

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add PostgreSQL addon**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

4. **Add Redis addon**:
   ```bash
   heroku addons:create heroku-redis:mini
   ```

5. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
   heroku config:set DEBUG=False
   ```

6. **Deploy**:
   ```bash
   git push heroku main
   ```

7. **Run migrations**:
   ```bash
   heroku run alembic upgrade head
   ```

### Render Deployment

1. Create account on render.com
2. Connect your GitHub repository
3. Create a new Web Service with these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL database service
5. Add Redis service
6. Set environment variables in Render dashboard

### Railway Deployment

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and deploy:
   ```bash
   railway login
   railway init
   railway add --service postgresql
   railway add --service redis
   railway deploy
   ```

### Environment Variables for Production

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port/0
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

## Scaling Considerations

### For High Load (500k+ records)
1. **Increase worker count**: Scale Celery workers horizontally
2. **Database optimization**: 
   - Use connection pooling
   - Optimize indexes
   - Consider read replicas
3. **Redis optimization**: 
   - Increase memory allocation
   - Use Redis cluster for high availability
4. **File handling**: 
   - Use cloud storage (AWS S3, etc.) for uploaded files
   - Implement chunked file processing

### Monitoring
- Use application monitoring (Sentry, DataDog, etc.)
- Monitor Celery tasks with Flower
- Set up database monitoring
- Configure log aggregation

### Security
- Use strong SECRET_KEY in production
- Configure HTTPS/SSL
- Implement rate limiting
- Set up proper CORS policies
- Use environment variables for sensitive data