# PowerShell Heroku Deployment Script for Product Importer

Write-Host "🚀 Starting Heroku deployment..." -ForegroundColor Green

# Check if Heroku CLI is installed
try {
    heroku --version | Out-Null
} catch {
    Write-Host "❌ Heroku CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
}

# Get app name from user
$AppName = Read-Host "Enter your Heroku app name"

if ([string]::IsNullOrWhiteSpace($AppName)) {
    Write-Host "❌ App name is required" -ForegroundColor Red
    exit 1
}

# Login to Heroku
Write-Host "📝 Please login to Heroku in the browser window..." -ForegroundColor Yellow
heroku login

# Create Heroku app
Write-Host "🏗️  Creating Heroku app: $AppName" -ForegroundColor Blue
try {
    heroku create $AppName
} catch {
    Write-Host "App might already exist, continuing..." -ForegroundColor Yellow
}

# Add PostgreSQL addon
Write-Host "🐘 Adding PostgreSQL addon..." -ForegroundColor Blue
try {
    heroku addons:create heroku-postgresql:mini -a $AppName
} catch {
    Write-Host "PostgreSQL addon might already exist" -ForegroundColor Yellow
}

# Add Redis addon
Write-Host "📡 Adding Redis addon..." -ForegroundColor Blue
try {
    heroku addons:create heroku-redis:mini -a $AppName
} catch {
    Write-Host "Redis addon might already exist" -ForegroundColor Yellow
}

# Generate and set secret key
Write-Host "🔐 Setting environment variables..." -ForegroundColor Blue
$SecretKey = [System.Web.Security.Membership]::GeneratePassword(32, 0)
heroku config:set SECRET_KEY=$SecretKey -a $AppName
heroku config:set DEBUG=false -a $AppName
heroku config:set ENVIRONMENT=production -a $AppName

# Deploy to Heroku
Write-Host "🚀 Deploying to Heroku..." -ForegroundColor Green
git push heroku main

# Scale workers
Write-Host "⚙️  Scaling workers..." -ForegroundColor Blue
heroku ps:scale web=1 webhook_worker=1 upload_worker=1 -a $AppName

# Run database migrations
Write-Host "🗄️  Running database migrations..." -ForegroundColor Blue
heroku run alembic upgrade head -a $AppName

# Show completion message
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 App URL: https://$AppName.herokuapp.com" -ForegroundColor Cyan
Write-Host "📊 View logs: heroku logs --tail -a $AppName" -ForegroundColor Cyan
Write-Host "⚙️  Manage app: https://dashboard.heroku.com/apps/$AppName" -ForegroundColor Cyan

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Visit your app URL to test"
Write-Host "2. Create webhooks pointing to webhook.site"
Write-Host "3. Test product operations and CSV uploads"
Write-Host "4. Monitor logs for any issues"

# Ask if user wants to open the app
$OpenApp = Read-Host "Open the app in browser? (y/N)"
if ($OpenApp -eq "y" -or $OpenApp -eq "Y") {
    heroku open -a $AppName
}