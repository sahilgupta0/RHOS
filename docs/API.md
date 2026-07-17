# RHOS API Reference

The RHOS backend exposes a REST API built using FastAPI. The complete interactive documentation is available locally at `http://localhost:8000/docs`.

## Base Configuration

- **Development Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`
- **Authorization**: `Bearer <token>` (Required for all protected endpoints)

## Endpoint Reference

### 1. Health & Status
- **`GET /health`**
  - Public endpoint to check backend health status, Firebase connection state, and Gemini configurations.

### 2. Authentication
- **`POST /auth/login`**
  - Payload: `{ "email": "...", "password": "..." }`
  - Response: Access token, token type, and user metadata profile.
- **`POST /auth/register`**
  - Payload: `{ "email": "...", "password": "...", "name": "...", "role": "doctor" }`
  - Response: Access token and user profile.
- **`GET /auth/me`**
  - Returns authenticated user details.

### 3. Patients
- **`GET /patients`**
  - Query Params: `search` (filter by name), `page` (default 1), `page_size` (default 20), `village_id`.
  - Response: List of patients, total count.
- **`GET /patient/{id}`**
  - Returns demographic details for a specific patient.
- **`GET /patient/history/{id}`**
  - Compiles the full history card: patient profile, past medical conditions, vitals log, and allergy details.
- **`POST /patient`**
  - Registers a new patient.

### 4. Consultations & AI Pipeline
- **`POST /consultation/start`**
  - Payload: `{ "patient_id": "...", "chief_complaint": "..." }`
- **`POST /consultation/chat`**
  - Feeds message into the multi-agent clinical decision support pipeline.
  - Payload: `{ "consultation_id": "...", "message": "...", "language": "en" }`
- **`POST /consultation/upload`**
  - Form Data: `consultation_id`, `file` (image).
  - Triggers the Gemini Vision agent.

### 5. Utilities & Services
- **`POST /triage`**
  - Triage classification endpoint.
- **`POST /medicine/check`**
  - Validates drug-drug and drug-allergy interactions.
- **`POST /summary`**
  - Compiles clinical summary notes.
- **`POST /speech-to-text`**
  - Multi-lingual audio processing.
- **`POST /upload`**
  - General file uploading to Storage.
