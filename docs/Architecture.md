# RHOS System Architecture

This document describes the high-level architecture of Rural Health OS (RHOS), component relationships, and data flows.

## Core Component Structure

RHOS is built as a three-tier system:
1. **Frontend (React 19 + TypeScript + Vite)**: User interface for clinicians, nurses, and ASHA workers. Uses Tailwind v4 and clean, professional design layouts with Light/Dark mode support.
2. **Backend (FastAPI + Pydantic v2 + Google ADK)**: Provides REST API endpoints, handles business logic, and orchestrates the AI agent pipeline.
3. **Database & Storage (Firebase Firestore & Firebase Storage)**: Non-relational real-time storage for medical records, patient demographics, and image media files.

```
┌─────────────────────────────────────────────────┐
│                   Frontend                       │
│         React 19 + ShadCN + Tailwind v4          │
│     Dashboard │ Consultation │ Analytics         │
└────────────────────┬────────────────────────────┘
                     │ REST API / JSON
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
                     │ AsyncClient
┌────────────────────┴────────────────────────────┐
│              Firebase                            │
│       Firestore │ Storage │ Auth                 │
└─────────────────────────────────────────────────┘
```

## Data Access Layer

We enforce **Clean Architecture** patterns:
- **Models**: Pydantic classes representing domain entities (`app/models/`).
- **Schemas**: Request/response serializers for validation (`app/schemas/`).
- **Repositories**: Encapsulate Firestore database queries and CRUD (`app/repositories/`).
- **Services**: Contain business rules and integrate third-party resources (Gemini, Speech, Maps) (`app/services/`).

## Data Flow: Consultation Pipeline

1. **Intake**: Clinician opens a new consultation. They speak or type symptoms.
2. **Agent Chain**:
   - **Conversation Agent** parses the text, extracts symptoms/duration/severity into a structured JSON payload.
   - **History Agent** compiles past conditions and allergies from the patient file.
   - **Triage Agent** assigns urgency (LOW / MEDIUM / HIGH) and flags anomalies.
   - **Vision Agent** (if image uploaded) describes visual anomalies.
   - **Medicine Agent** cross-references prescriptions against known drug-drug and allergy conflicts.
   - **Doctor Agent** summarizes the session.
   - **Follow-up Agent** generates follow-up steps.
3. **Verification**: Clinician edits and approves the clinical summary and prescription details.
