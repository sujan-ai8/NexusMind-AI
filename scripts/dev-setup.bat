@echo off
echo ==========================================
echo    NexusMind AI - Phase 1 Environment Setup
echo ==========================================

echo [1/3] Copying environment template...
if not exist .env copy .env.example .env

echo [2/3] Installing Python backend dependencies...
python -m pip install --upgrade pip
pip install -r apps\api\requirements.txt

echo [3/3] Installing Web frontend dependencies...
cd apps\web
npm install
cd ..

echo Setup complete! Run:
echo   python -m uvicorn apps.api.app.main:app --reload (Terminal 1)
echo   cd apps\web ^&^& npm run dev (Terminal 2)

