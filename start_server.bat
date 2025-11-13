@echo off
echo Starting Product Importer FastAPI Server...
echo.

cd /d "C:\Projects\Product_Importer"
call ".venv\Scripts\activate.bat"

echo FastAPI Server Starting on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause