"""
RHOS Consultation Models.

Data models for consultations, triage, vision results, and doctor notes.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from app.models.common import FirestoreDocument, TimestampMixin, TriagePriority


class Consultation(FirestoreDocument, TimestampMixin):
    """A single consultation session."""

    patient_id: str
    patient_name: str = ""
    doctor_id: str = ""
    doctor_name: str = ""
    visit_id: str = ""
    chief_complaint: str = ""
    symptoms: list[dict[str, Any]] = Field(default_factory=list)
    duration: str = ""
    severity: str = ""
    conversation_history: list[dict[str, str]] = Field(default_factory=list)
    triage_priority: TriagePriority | None = None
    triage_reasoning: str = ""
    history_summary: str = ""
    clinical_summary: str = ""
    vision_results: list[dict[str, Any]] = Field(default_factory=list)
    medication_checks: list[dict[str, Any]] = Field(default_factory=list)
    follow_up_plan: str = ""
    follow_up_date: datetime | None = None
    status: str = "active"  # active, completed, cancelled
    language: str = "en"


class TriageLog(FirestoreDocument, TimestampMixin):
    """Log of a triage classification decision."""

    consultation_id: str
    patient_id: str
    priority: TriagePriority
    reasoning: str = ""
    symptoms_considered: list[str] = Field(default_factory=list)
    vitals_considered: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0
    agent_model: str = ""


class VisionResult(FirestoreDocument, TimestampMixin):
    """Result from medical image analysis."""

    consultation_id: str
    patient_id: str
    image_url: str
    image_type: str = ""  # e.g., "skin_lesion", "wound", "x-ray"
    findings: str = ""
    description: str = ""
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    disclaimer: str = "AI-generated description only. Not a medical diagnosis."


class DoctorNote(FirestoreDocument, TimestampMixin):
    """Doctor's clinical note for a consultation."""

    consultation_id: str
    patient_id: str
    doctor_id: str = ""
    summary: str = ""
    assessment: str = ""
    plan: str = ""
    prescriptions: list[dict[str, Any]] = Field(default_factory=list)
    follow_up_instructions: str = ""
    referral_needed: bool = False
    referral_details: str = ""
    signed: bool = False
    signed_at: datetime | None = None
