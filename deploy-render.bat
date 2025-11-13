@echo off
echo =========================================
echo Product Importer - Render Deployment
echo =========================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git repository not initialized!
    echo Please run: git init ^&^& git add . ^&^& git commit -m "Initial commit"
    pause
    exit /b 1
)

echo ✅ Git repository ready
echo.

REM Check if render.yaml exists
if not exist "render.yaml" (
    echo ❌ render.yaml not found!
    echo Please ensure render.yaml is in the project root
    pause
    exit /b 1
)

echo ✅ Render configuration found
echo.

REM Check for uncommitted changes and commit them
git diff-index --quiet HEAD -- >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  You have uncommitted changes. Committing them now...
    git add .
    git commit -m "Add Render deployment configuration"
)

echo 🚀 Ready for Render deployment!
echo.
echo Next steps:
echo 1. Push changes to GitHub:
echo    git push origin main
echo.
echo 2. Go to https://render.com/dashboard
echo 3. Click "New" → "Blueprint"
echo 4. Connect your GitHub account
echo 5. Select repository: "product-importer"
echo 6. Click "Apply" to deploy all services
echo.
echo Services that will be created:
echo   📱 Web Service: FastAPI application
echo   🔄 Webhook Worker: Fast webhook processing
echo   📁 Upload Worker: Large file handling
echo   🗄️  PostgreSQL: Database
echo   🔴 Redis: Task queues
echo.
echo Total deployment time: ~5-10 minutes
echo =========================================
pause