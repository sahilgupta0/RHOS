# 🏥 Rural Health OS (RHOS)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28.svg)](https://firebase.google.com/)

> **AI-powered Clinical Decision Support & Care Coordination System for Rural Primary Healthcare**

RHOS assists healthcare professionals in rural Indian primary health centers with intelligent clinical decision support. It uses 8 specialized AI agents orchestrated via Google ADK to help with triage, medication safety, clinical summaries, and follow-up planning.

> ⚠️ **Important:** RHOS is a Clinical Decision Support System (CDSS) — it is **NOT** an AI doctor. All medical decisions are made by qualified healthcare professionals. AI outputs are advisory only.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│         React 19 + ShadCN + Tailwind v4          │
│     Dashboard │ Consultation │ Analytics         │
└────────────────────┬────────────────────────────┘
                     │ REST API
┌────────────────────┴────────────────────────────┐
│                   Backend                        │
│              FastAPI + Pydantic                   │
│  ┌─────────────────────────────────────────┐     │
│  │         AI Agent Pipeline (ADK)          │     │
│  │  Conversation → History → Triage →       │     │
│  │  Vision → Medicine → Doctor → Follow-up  │     │
│  └─────────────────────────────────────────┘     │
│         Services │ Repositories                   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────┐
│              Firebase                            │
│       Firestore │ Storage │ Auth                 │
└─────────────────────────────────────────────────┘
```

## ✨ Key Features

- **AI-Powered Consultation** — Chat-based consultation with multi-agent pipeline
- **Smart Triage** — Automatic priority classification (LOW / MEDIUM / HIGH)
- **Medication Safety** — Drug interaction checks, allergy warnings, generic alternatives
- **Voice Input** — Browser-native speech-to-text for hands-free input
- **Medical Image Analysis** — Upload and analyze medical images
- **Clinical Summaries** — Auto-generated doctor notes and follow-up plans
- **Analytics Dashboard** — Patient trends, disease distribution, village statistics
- **Dark Mode** — Full dark/light theme support
- **Offline-Ready** — Graceful degradation when AI services are unavailable

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Node.js 22+**
- **Firebase Project** with Firestore and Storage enabled
- **Google Gemini API Key**

### 1. Clone & Setup

```bash
git clone <repository-url>
cd RHOS

# Windows
.\scripts\setup.ps1

# Linux/Mac
chmod +x scripts/setup.sh && ./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your backend URL
```

### 3. Seed Database

```bash
cd backend
python -m scripts.seed_mongodb
```

### 4. Run Development Servers

```bash
# Terminal 1 — Backend
cd backend
source venv/bin/activate  # or .\venv\Scripts\Activate on Windows
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

### 5. Open Application

- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 🐳 Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 📁 Project Structure

```
RHOS/
├── backend/
│   ├── app/
│   │   ├── agents/          # 8 AI agents (ADK)
│   │   ├── api/             # FastAPI route handlers
│   │   ├── core/            # Security, Firebase init, logging
│   │   ├── middleware/       # CORS, error handling, logging
│   │   ├── models/          # Pydantic data models
│   │   ├── prompts/         # Agent prompt templates
│   │   ├── repositories/    # Firestore data access
│   │   ├── schemas/         # Request/response schemas
│   │   └── services/        # Business logic layer
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # API client modules
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React contexts
│   │   ├── hooks/           # Custom hooks
│   │   ├── pages/           # Route pages
│   │   ├── styles/          # Global styles
│   │   └── types/           # TypeScript types
│   ├── Dockerfile
│   └── nginx.conf
├── datasets/                # 12 synthetic CSV datasets
├── docs/                    # Documentation
├── scripts/                 # Setup & seed scripts
└── docker-compose.yml
```

## 📊 Datasets

12 synthetic CSV datasets with realistic Indian rural healthcare data:

| Dataset | Records | Description |
|---------|---------|-------------|
| patients | 300 | Patient demographics |
| medical_history | 400 | Past conditions & diagnoses |
| visits | 500 | Visit records |
| vitals | 500 | Vital signs measurements |
| medicines | 200 | Drug database with interactions |
| allergies | 250 | Patient allergies |
| hospitals | 30 | Hospital directory |
| asha_workers | 50 | Community health workers |
| villages | 40 | Village demographics |
| appointments | 400 | Scheduled appointments |
| referrals | 200 | Hospital referrals |
| symptoms | 300 | Symptom database |

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `FIREBASE_CREDENTIALS` | Yes | Path to Firebase service account JSON |
| `AUTH_MODE` | No | `firebase` (default) or `local` |
| `GOOGLE_MAPS_API_KEY` | No | For maps features |
| `CORS_ORIGINS` | No | Allowed CORS origins |

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Google ADK](https://google.github.io/adk-docs/) for AI agent orchestration
- [Gemini 2.5 Pro](https://deepmind.google/technologies/gemini/) for clinical reasoning
- Inspired by India's rural primary healthcare system and ASHA worker program
