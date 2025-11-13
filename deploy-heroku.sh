#!/bin/bash

# Production deployment script for Product Importer
# This script deploys the application to Heroku

set -e

echo "🚀 Starting deployment to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku whoami &> /dev/null; then
    echo "❌ Please login to Heroku first: heroku login"
    exit 1
fi

# Get app name from user or use default
read -p "Enter Heroku app name (or press Enter for 'product-importer-acme'): " APP_NAME
APP_NAME=${APP_NAME:-product-importer-acme}

echo "📱 Creating Heroku app: $APP_NAME"

# Create Heroku app (will fail gracefully if exists)
heroku create $APP_NAME || echo "App already exists, continuing..."

# Add PostgreSQL addon
echo "🐘 Adding PostgreSQL database..."
heroku addons:create heroku-postgresql:mini -a $APP_NAME || echo "PostgreSQL already exists"

# Add Redis addon
echo "🔴 Adding Redis cache..."
heroku addons:create heroku-redis:mini -a $APP_NAME || echo "Redis already exists"

# Generate and set secret key
echo "🔐 Setting up environment variables..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
heroku config:set SECRET_KEY="$SECRET_KEY" -a $APP_NAME

# Set other environment variables
heroku config:set DEBUG=False -a $APP_NAME
heroku config:set ALLOWED_HOSTS="$APP_NAME.herokuapp.com" -a $APP_NAME

# Add git remote if not exists
if ! git remote get-url heroku &> /dev/null; then
    heroku git:remote -a $APP_NAME
fi

# Deploy to Heroku
echo "🚢 Deploying to Heroku..."
git push heroku main

# Run database migrations
echo "🗃️ Running database migrations..."
heroku run alembic upgrade head -a $APP_NAME

# Scale dynos
echo "⚡ Scaling dynos..."
heroku ps:scale web=1 webhook_worker=1 upload_worker=1 -a $APP_NAME

# Open the app
echo "✅ Deployment complete!"
echo "🌍 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📊 Admin panel: https://$APP_NAME.herokuapp.com/docs"
echo "🔍 Logs: heroku logs --tail -a $APP_NAME"

# Ask if user wants to open the app
read -p "Open the app in browser? (y/N): " OPEN_APP
if [[ $OPEN_APP =~ ^[Yy]$ ]]; then
    heroku open -a $APP_NAME
fi

echo "🎉 Deployment successful!"