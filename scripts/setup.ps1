# RHOS Windows Setup Script
# Run this from the root of the RHOS workspace

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🏥 Setting up Rural Health OS (RHOS)..." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Setup Backend Python Virtual Environment
Write-Host "`n[1/4] Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "backend\venv")) {
    python -m venv backend\venv
    Write-Host "Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists. Skipping creation." -ForegroundColor Yellow
}

# Activate virtual environment and install requirements
Write-Host "`n[2/4] Installing backend dependencies..." -ForegroundColor Yellow
& "backend\venv\Scripts\pip" install -r backend\requirements.txt

# 2. Generate Synthetic Datasets
Write-Host "`n[3/4] Generating synthetic CSV datasets..." -ForegroundColor Yellow
& "backend\venv\Scripts\python" scripts\generate_datasets.py

# 3. Setup Frontend Node modules
Write-Host "`n[4/4] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..

Write-Host "`n=========================================" -ForegroundColor Green
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "To run RHOS:" -ForegroundColor Green
Write-Host "1. Edit backend\.env (from backend\.env.example)" -ForegroundColor Cyan
Write-Host "2. Start Backend: cd backend; .\venv\Scripts\activate; uvicorn app.main:app --reload --port 8000" -ForegroundColor Cyan
Write-Host "3. Start Frontend: cd frontend; npm run dev" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Green
