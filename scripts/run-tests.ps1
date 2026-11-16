# NexusMind AI - Run Automated Tests
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Running NexusMind AI Phase 1 Test Suite " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Run Backend Pytest
Write-Host "[1/2] Executing Backend Pytest suite..." -ForegroundColor Green
$env:DATABASE_URL = "sqlite:///:memory:"
$env:ENVIRONMENT = "testing"
$env:SECRET_KEY = "test-secret-key-phase1-validation-min32chars"
python -m pytest apps/api/tests -v --tb=short

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend tests failed!" -ForegroundColor Red
    exit 1
}

# 2. Run Frontend Build Check
Write-Host "[2/2] Verifying Frontend TypeScript & Bundle..." -ForegroundColor Green
Push-Location apps\web
npm run build
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "All Phase 1 tests passed successfully!" -ForegroundColor Green

