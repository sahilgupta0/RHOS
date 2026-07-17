#!/bin/bash
# RHOS Unix/Mac Setup Script
# Run this from the root of the RHOS workspace

set -e

echo -e "\033[0;36m=========================================\033[0m"
echo -e "\033[0;36m🏥 Setting up Rural Health OS (RHOS)...\033[0m"
echo -e "\033[0;36m=========================================\033[0m"

# 1. Setup Backend Python Virtual Environment
echo -e "\n\033[0;33m[1/4] Setting up Python virtual environment...\033[0m"
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
    echo -e "\033[0;32mVirtual environment created.\033[0m"
else
    echo -e "\033[0;33mVirtual environment already exists. Skipping creation.\033[0m"
fi

# Activate virtual environment and install requirements
echo -e "\n\033[0;33m[2/4] Installing backend dependencies...\033[0m"
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2. Generate Synthetic Datasets
echo -e "\n\033[0;33m[3/4] Generating synthetic CSV datasets...\033[0m"
python scripts/generate_datasets.py

# 3. Setup Frontend Node modules
echo -e "\n\033[0;33m[4/4] Installing frontend dependencies...\033[0m"
cd frontend
npm install
cd ..

echo -e "\n\033[0;32m=========================================\033[0m"
echo -e "\033[0;32m🎉 Setup completed successfully!\033[0m"
echo -e "To run RHOS:"
echo -e "1. Edit backend/.env (from backend/.env.example)"
echo -e "2. Start Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo -e "3. Start Frontend: cd frontend && npm run dev"
echo -e "\033[0;32m=========================================\033[0m"
