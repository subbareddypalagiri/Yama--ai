@echo off
REM YAMA AI Backend Startup Script
REM Run this to start the backend server

cls
echo.
echo ================================================================================
echo                    YAMA AI - BACKEND STARTUP SCRIPT
echo ================================================================================
echo.
echo Starting YAMA AI Backend Server...
echo.

REM Navigate to backend directory
cd /d "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend" || (
    echo ERROR: Could not navigate to backend directory
    pause
    exit /b 1
)

echo [OK] Navigated to backend directory
echo.

REM Check if venv exists
if not exist "venv\Scripts\Activate.ps1" (
    echo [ERROR] Virtual environment not found!
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [OK] Virtual environment found
echo.

REM Activate virtual environment and start server
echo [INFO] Activating virtual environment...
echo [INFO] Starting uvicorn server on port 8000...
echo.
echo ================================================================================
echo Backend will start below. Press CTRL+C to stop.
echo ================================================================================
echo.

REM Start the backend
python -m uvicorn main:app --reload --port 8000

pause
