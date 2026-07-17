# Firebase Firestore & Storage Configuration

RHOS integrates with Firebase for data persistence and media storage.

## Firestore Collections & Schema

### 1. `patients`
Stores demographics, location metadata, and assigned health workers.
- Schema: `id`, `name`, `age`, `gender`, `blood_group`, `phone`, `village_id`, `asha_worker_id`, `aadhaar` (masked), `is_active`, `created_at`, `updated_at`.

### 2. `medical_history`
Chronological list of chronic conditions, past diseases, and major procedures.
- Schema: `id`, `patient_id`, `condition`, `diagnosed_date`, `status` (active/resolved/chronic), `notes`.

### 3. `visits`
Tracks patient check-in history.
- Schema: `id`, `patient_id`, `date`, `type` (walk-in/appointment), `chief_complaint`, `doctor_id`.

### 4. `vitals`
Historical vital measurements.
- Schema: `id`, `patient_id`, `visit_id`, `bp_systolic`, `bp_diastolic`, `heart_rate`, `temperature` (°C), `spo2`, `weight`, `recorded_at`.

### 5. `consultations`
Sessions managed by the AI agent pipeline.
- Schema: `id`, `patient_id`, `chief_complaint`, `triage_priority`, `clinical_summary`, `follow_up_plan`, `status` (active/completed).

### 6. `medicines`
Indian generic and brand names medicine master dataset.

### 7. `allergies`
Patient allergies and severity logs.

## Security Rules (Firestore)

Deploy these rules to secure access to patient data:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      // Enforce authentication for read/write operations
      allow read, write: if request.auth != null;
    }
  }
}
```

## Storage Structure

Files are organized in folders:
- `/uploads/`: Medical images and patient uploads.
- `/reports/`: Exported summary PDFs.
