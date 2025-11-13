@echo off
echo Starting Product Importer Celery Worker...
echo.

cd /d "C:\Projects\Product_Importer"
call ".venv\Scripts\activate.bat"

echo Celery Worker Starting...
echo Press Ctrl+C to stop
echo.

python -m celery -A app.celery worker --loglevel=info --pool=solo

pause