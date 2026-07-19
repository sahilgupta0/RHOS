"""
RHOS API Schemas.

Pydantic v2 request/response schemas for API validation and serialization.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.common import (
    BloodGroup,
    Gender,
    TriagePriority,
    UserRole,
)

# ── Auth Schemas ───────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: UserRole = UserRole.DOCTOR
    phone: str = ""
    hospital_id: str = ""


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse | None = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    phone: str = ""
    hospital_name: str = ""
    avatar_url: str = ""
    is_active: bool = True
    patient_id: str = ""


# ── Patient Schemas ────────────────────────────────────────────────────────────


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: Gender
    date_of_birth: date | None = None
    blood_group: BloodGroup | None = None
    phone: str = ""
    address: str = ""
    village_id: str = ""
    village_name: str = ""
    district: str = ""
    asha_worker_id: str = ""
    emergency_contact: str = ""


class PatientUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    phone: str | None = None
    address: str | None = None
    village_id: str | None = None
    emergency_contact: str | None = None
    is_active: bool | None = None


class PatientResponse(BaseModel):
    id: str
    name: str
    age: int
    gender: Gender
    date_of_birth: date | None = None
    blood_group: BloodGroup | None = None
    phone: str = ""
    address: str = ""
    village_id: str = ""
    village_name: str = ""
    district: str = ""
    asha_worker_id: str = ""
    is_active: bool = True
    created_at: datetime | None = None


class PatientListResponse(BaseModel):
    patients: list[PatientResponse] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20


# ── Consultation Schemas ───────────────────────────────────────────────────────


class ConsultationStartRequest(BaseModel):
    patient_id: str
    chief_complaint: str = ""
    language: str = "en"


class ConsultationChatRequest(BaseModel):
    consultation_id: str
    message: str
    language: str = "en"


class ConsultationSubmitRequest(BaseModel):
    consultation_id: str


class ConsultationChatResponse(BaseModel):
    consultation_id: str
    agent_response: str = ""
    symptoms_extracted: list[dict[str, Any]] = Field(default_factory=list)
    triage_priority: TriagePriority | None = None
    triage_reasoning: str = ""
    history_summary: str = ""
    clinical_summary: str = ""
    medication_checks: list[dict[str, Any]] = Field(default_factory=list)
    follow_up_plan: str = ""
    ready_to_submit: bool = False
    agent_pipeline_status: dict[str, str] = Field(default_factory=dict)


class ConsultationResponse(BaseModel):
    id: str
    patient_id: str
    patient_name: str = ""
    doctor_name: str = ""
    chief_complaint: str = ""
    triage_priority: TriagePriority | None = None
    triage_reasoning: str = ""
    status: str = "active"
    clinical_summary: str = ""
    follow_up_plan: str = ""
    conversation_history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime | None = None


# ── Triage Schemas ─────────────────────────────────────────────────────────────


class TriageRequest(BaseModel):
    patient_id: str
    symptoms: list[str]
    vitals: dict[str, Any] = Field(default_factory=dict)
    medical_history: list[str] = Field(default_factory=list)
    age: int | None = None
    gender: str | None = None


class TriageResponse(BaseModel):
    priority: TriagePriority
    reasoning: str = ""
    confidence: float = 0.0
    recommendations: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "AI-assisted triage. Final assessment by qualified medical professional required."
    )


# ── Medicine Schemas ───────────────────────────────────────────────────────────


class MedicineCheckRequest(BaseModel):
    medications: list[str]
    patient_id: str | None = None
    allergies: list[str] = Field(default_factory=list)
    current_medications: list[str] = Field(default_factory=list)
    age: int | None = None
    conditions: list[str] = Field(default_factory=list)


class MedicineCheckResponse(BaseModel):
    interactions: list[dict[str, Any]] = Field(default_factory=list)
    allergy_warnings: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    safe_to_prescribe: bool = True
    disclaimer: str = (
        "AI-assisted medication review. Pharmacist/physician verification required."
    )


# ── Vision Schemas ─────────────────────────────────────────────────────────────


class VisionAnalysisResponse(BaseModel):
    image_url: str = ""
    findings: str = ""
    description: str = ""
    recommendations: list[str] = Field(default_factory=list)
    disclaimer: str = "AI-generated image description only. Not a medical diagnosis."


# ── Speech Schemas ─────────────────────────────────────────────────────────────


class SpeechToTextResponse(BaseModel):
    text: str
    confidence: float = 0.0
    language: str = "en"


class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"
    voice: str = "default"


# ── Summary Schemas ────────────────────────────────────────────────────────────


class SummaryRequest(BaseModel):
    consultation_id: str
    include_recommendations: bool = True


class SummaryResponse(BaseModel):
    consultation_id: str
    summary: str = ""
    assessment: str = ""
    plan: str = ""
    follow_up: str = ""
    disclaimer: str = (
        "AI-generated clinical summary. Review and approval by treating physician required."
    )


# ── Upload Schemas ─────────────────────────────────────────────────────────────


class UploadResponse(BaseModel):
    file_url: str
    file_name: str
    content_type: str = ""
    size_bytes: int = 0


# ── Generic Schemas ────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = ""
    firebase_connected: bool = False
    gemini_configured: bool = False


class ErrorResponse(BaseModel):
    detail: str
    status_code: int = 500
    error_type: str = "internal_error"


class MessageResponse(BaseModel):
    message: str
    success: bool = True
