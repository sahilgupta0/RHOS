# Local Development Setup Guide

Follow this guide to configure and run RHOS on your local development system.

## System Prerequisites

- **Python**: 3.12 or higher installed.
- **Node.js**: 22 or higher installed.
- **Git**
- **Docker** (optional, for container runs)

## Setup Steps

### 1. Backend Configuration

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create your Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Copy environment file template and configure:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and fill in `GEMINI_API_KEY`. By default, `AUTH_MODE` is set to `local` so you do not need Firebase keys to run locally for demos.

### 2. Dataset Generation & Database Seeding

1. From the project root, generate the synthetic CSV datasets:
   ```bash
   python scripts/generate_datasets.py
   ```
2. (Optional) If you have configured a Firebase project in `.env`, seed the data to Firestore:
   ```bash
   python scripts/seed_firestore.py
   ```

### 3. Frontend Configuration

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Copy environment template:
   ```bash
   cp .env.example .env
   ```

## Running the Application

### Backend Service
Start the FastAPI server:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
Visit API Documentation at `http://localhost:8000/docs`.

### Frontend Dev Server
Start the Vite React dev server:
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser. Login using the credentials shown in the login screen.
