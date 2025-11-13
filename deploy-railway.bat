@echo off
echo =========================================
echo Product Importer - Railway Deployment
echo =========================================
echo.

REM Check if Node.js is installed for Railway CLI
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Railway CLI using PowerShell method...
    powershell -Command "iwr https://railway.app/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Railway CLI
        echo Please install manually from: https://docs.railway.app/develop/cli
        pause
        exit /b 1
    )
) else (
    echo Installing Railway CLI using npm...
    npm install -g @railway/cli
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Railway CLI via npm
        pause
        exit /b 1
    )
)

echo ✅ Railway CLI installed
echo.

echo 🚀 Starting Railway deployment...
echo.

echo Step 1: Login to Railway
railway login
if %errorlevel% neq 0 (
    echo ❌ Railway login failed
    pause
    exit /b 1
)

echo.
echo Step 2: Link GitHub repository (recommended)
railway link
echo.

echo Step 3: Deploy application
railway up
if %errorlevel% neq 0 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

echo.
echo =========================================
echo 🎉 Deployment Complete!
echo =========================================
echo.
echo Your app is now deployed on Railway!
echo.
echo Next steps:
echo 1. Check Railway dashboard for your app URL
echo 2. Railway will auto-add PostgreSQL and Redis
echo 3. Your webhook workers will start automatically
echo.
echo To view your app:
echo   railway open
echo.
echo To view logs:
echo   railway logs
echo.
echo To add database (if not auto-added):
echo   railway add postgresql
echo   railway add redis
echo.
pause