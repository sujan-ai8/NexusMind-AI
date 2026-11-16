# NexusMind AI - Run Local Services (PowerShell)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   NexusMind AI - Phase 1 Local Launcher  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in background
Write-Host "[1/2] Starting FastAPI Backend on http://localhost:8000..." -ForegroundColor Green
$BackendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000 --reload" -PassThru

# 2. Start Vite Frontend
Write-Host "[2/2] Starting Vite Frontend on http://localhost:5173..." -ForegroundColor Green
Set-Location apps\web
npm run dev

