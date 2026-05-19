# YAMA AI Backend Startup Script (PowerShell)
# Run this with: powershell -ExecutionPolicy RemoteSigned -File START_BACKEND.ps1

Clear-Host

Write-Host ""
Write-Host "=" * 80
Write-Host "YAMA AI - BACKEND STARTUP SCRIPT (PowerShell)" -ForegroundColor Green
Write-Host "=" * 80
Write-Host ""

Write-Host "Starting YAMA AI Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$backendPath = "c:\Users\subba\OneDrive\Desktop\project -car\Yama - ai\backend"
Write-Host "[STEP 1] Navigating to backend directory..." -ForegroundColor Yellow

if (-Not (Test-Path $backendPath)) {
    Write-Host "[ERROR] Backend directory not found!" -ForegroundColor Red
    Write-Host "Expected path: $backendPath" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location $backendPath
Write-Host "[OK] Navigated to: $backendPath" -ForegroundColor Green
Write-Host ""

# Check if venv exists
Write-Host "[STEP 2] Checking virtual environment..." -ForegroundColor Yellow

if (-Not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Virtual environment found" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "[STEP 3] Activating virtual environment..." -ForegroundColor Yellow

try {
    & ".\venv\Scripts\Activate.ps1"
    Write-Host "[OK] Virtual environment activated" -ForegroundColor Green
    Write-Host "Prompt should show: (venv)" -ForegroundColor Cyan
} catch {
    Write-Host "[ERROR] Could not activate virtual environment" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if fastapi/uvicorn is installed
Write-Host "[STEP 4] Checking dependencies..." -ForegroundColor Yellow

$checkImport = python -c "import uvicorn; print('OK')" 2>&1
if ($checkImport -notlike "*OK*") {
    Write-Host "[WARNING] Uvicorn not found, installing..." -ForegroundColor Yellow
    pip install -q uvicorn
}

Write-Host "[OK] All dependencies ready" -ForegroundColor Green
Write-Host ""

# Display startup info
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Backend Configuration:" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "  Host: 127.0.0.1" -ForegroundColor White
Write-Host "  Port: 8000" -ForegroundColor White
Write-Host "  URL: http://localhost:8000" -ForegroundColor White
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Database:" -ForegroundColor Cyan
Write-Host "  Documents: 398" -ForegroundColor White
Write-Host "  Acts: 85" -ForegroundColor White
Write-Host "  Categories: 14" -ForegroundColor White
Write-Host ""
Write-Host "Status: " -ForegroundColor Cyan -NoNewline
Write-Host "READY TO START" -ForegroundColor Green
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Start the backend
Write-Host "[STEP 5] Starting Uvicorn server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Server is starting below. Press CTRL+C to stop." -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""

# Run uvicorn
try {
    uvicorn main:app --reload --port 8000
} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to start server: $_" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
