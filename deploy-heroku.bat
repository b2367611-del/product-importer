@echo off
echo ========================================
echo Product Importer - Heroku Deployment
echo ========================================

echo.
echo Checking prerequisites...

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

where heroku >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Heroku CLI is not installed or not in PATH
    echo Please install Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

echo Prerequisites OK!
echo.

set /p APP_NAME="Enter your Heroku app name (e.g., my-product-importer): "
if "%APP_NAME%"=="" (
    echo ERROR: App name cannot be empty
    pause
    exit /b 1
)

echo.
echo Creating Heroku app: %APP_NAME%
heroku create %APP_NAME%
if %errorlevel% neq 0 (
    echo ERROR: Failed to create Heroku app
    pause
    exit /b 1
)

echo.
echo Adding PostgreSQL addon...
heroku addons:create heroku-postgresql:mini -a %APP_NAME%

echo.
echo Adding Redis addon...
heroku addons:create heroku-redis:mini -a %APP_NAME%

echo.
echo Setting environment variables...
heroku config:set SECRET_KEY="%RANDOM%%RANDOM%%RANDOM%" -a %APP_NAME%
heroku config:set ENVIRONMENT="production" -a %APP_NAME%

echo.
echo Deploying application...
git push heroku main
if %errorlevel% neq 0 (
    echo ERROR: Failed to deploy to Heroku
    pause
    exit /b 1
)

echo.
echo Scaling workers...
heroku ps:scale web=1 webhook_worker=1 upload_worker=1 -a %APP_NAME%

echo.
echo Initializing database...
heroku run python -c "from app.database import init_db; init_db()" -a %APP_NAME%

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your app is available at: https://%APP_NAME%.herokuapp.com
echo.
echo To view logs: heroku logs --tail -a %APP_NAME%
echo To open app: heroku open -a %APP_NAME%
echo.
pause