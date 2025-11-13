# Setup script for local development
# Run this after installing PostgreSQL and Memurai

Write-Host "🚀 Setting up Product Importer local environment..." -ForegroundColor Green

# Add PostgreSQL to PATH for this session
$env:PATH += ";C:\Program Files\PostgreSQL\17\bin"

# Check if Memurai is running
Write-Host "🔍 Checking Memurai (Redis) service..." -ForegroundColor Yellow
try {
    $memuraiService = Get-Service -Name "Memurai*" -ErrorAction SilentlyContinue
    if ($memuraiService) {
        if ($memuraiService.Status -ne "Running") {
            Start-Service $memuraiService.Name
            Write-Host "✅ Started Memurai service" -ForegroundColor Green
        } else {
            Write-Host "✅ Memurai is already running" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠️ Memurai service not found. Please start Memurai manually." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Could not check Memurai service. Please start it manually." -ForegroundColor Yellow
}

# Test Redis connection
Write-Host "🔗 Testing Redis connection..." -ForegroundColor Yellow
try {
    # Try to connect to Redis on default port
    $testConnection = Test-NetConnection -ComputerName "localhost" -Port 6379 -InformationLevel Quiet
    if ($testConnection) {
        Write-Host "✅ Redis is accessible on port 6379" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Redis not accessible on port 6379. Please check Memurai installation." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Could not test Redis connection" -ForegroundColor Yellow
}

# For PostgreSQL, let's use a simpler approach - try to connect without password first
Write-Host "🔍 Testing PostgreSQL connection..." -ForegroundColor Yellow

# Try connecting to create database (this might prompt for password)
Write-Host "📝 Attempting to create database..." -ForegroundColor Yellow
Write-Host "If prompted for password, try: postgres, admin, or the password you set during installation" -ForegroundColor Cyan

# Let's try with different common default passwords
$commonPasswords = @("", "postgres", "admin", "password")
$connected = $false

foreach ($pwd in $commonPasswords) {
    try {
        if ($pwd -eq "") {
            $result = & psql -U postgres -h localhost -c "SELECT 1;" 2>$null
        } else {
            $env:PGPASSWORD = $pwd
            $result = & psql -U postgres -h localhost -c "SELECT 1;" 2>$null
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Connected to PostgreSQL successfully!" -ForegroundColor Green
            
            # Create database
            if ($pwd -eq "") {
                & psql -U postgres -h localhost -c "CREATE DATABASE product_importer;" 2>$null
            } else {
                $env:PGPASSWORD = $pwd
                & psql -U postgres -h localhost -c "CREATE DATABASE product_importer;" 2>$null
            }
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Database 'product_importer' created successfully!" -ForegroundColor Green
            } else {
                Write-Host "ℹ️ Database might already exist (this is OK)" -ForegroundColor Blue
            }
            
            # Update .env file with working connection
            $dbUrl = "postgresql://postgres:$pwd@localhost:5432/product_importer"
            $envContent = Get-Content ".env" -Raw
            $envContent = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=$dbUrl"
            Set-Content ".env" $envContent
            Write-Host "✅ Updated .env file with database connection" -ForegroundColor Green
            
            $connected = $true
            break
        }
    } catch {
        continue
    }
}

if (-not $connected) {
    Write-Host "❌ Could not connect to PostgreSQL automatically" -ForegroundColor Red
    Write-Host "Please manually create the database using pgAdmin or psql:" -ForegroundColor Yellow
    Write-Host "1. Open pgAdmin or connect via psql" -ForegroundColor Yellow
    Write-Host "2. Run: CREATE DATABASE product_importer;" -ForegroundColor Yellow
    Write-Host "3. Update the DATABASE_URL in .env file with correct password" -ForegroundColor Yellow
}

Write-Host "" -ForegroundColor White
Write-Host "🎯 Next steps:" -ForegroundColor Green
Write-Host "1. Run database migrations: python -m alembic upgrade head" -ForegroundColor Yellow
Write-Host "2. Start the web server: python -m uvicorn app.main:app --reload" -ForegroundColor Yellow  
Write-Host "3. In another terminal, start Celery worker: python -m celery -A app.celery worker --loglevel=info" -ForegroundColor Yellow
Write-Host "4. Open http://localhost:8000 in your browser" -ForegroundColor Yellow

Remove-Variable PGPASSWORD -ErrorAction SilentlyContinue