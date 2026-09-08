# ==============================================================================
# FormMind AI - Production Launch Script (Windows PowerShell)
# ==============================================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  FormMind AI - Production Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Set Production Environment Variables
$env:ENVIRONMENT = "production"
$env:DEBUG = "false"

# Verify Virtual Environment
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activating Python Virtual Environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found in .\venv. Using system Python." -ForegroundColor Yellow
}

# Start Production ASGI Server
Write-Host "Starting Uvicorn ASGI Server on http://0.0.0.0:8000..." -ForegroundColor Green
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 2
