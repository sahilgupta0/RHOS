"""
RHOS Patient Models.

Data models for patients, medical history, vitals, and allergies.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from app.models.common import (
    AllergySeverity,
    BloodGroup,
    FirestoreDocument,
    Gender,
    MedicalConditionStatus,
    TimestampMixin,
)


class Patient(FirestoreDocument, TimestampMixin):
    """Patient demographic and identification data."""
    name: str
    age: int
    gender: Gender
    date_of_birth: date | None = None
    blood_group: BloodGroup | None = None
    phone: str = ""
    aadhaar: str = ""  # Masked for privacy
    address: str = ""
    village_id: str = ""
    village_name: str = ""
    district: str = ""
    state: str = "Rajasthan"
    asha_worker_id: str = ""
    emergency_contact: str = ""
    photo_url: str = ""
    is_active: bool = True


class MedicalHistory(FirestoreDocument, TimestampMixin):
    """Patient medical history entry."""
    patient_id: str
    condition: str
    diagnosed_date: date | None = None
    status: MedicalConditionStatus = MedicalConditionStatus.ACTIVE
    treating_doctor: str = ""
    hospital: str = ""
    notes: str = ""
    medications: list[str] = Field(default_factory=list)


class Vital(FirestoreDocument):
    """Patient vital signs measurement."""
    patient_id: str
    visit_id: str = ""
    recorded_at: datetime = Field(default_factory=datetime.now)
    bp_systolic: int | None = None
    bp_diastolic: int | None = None
    heart_rate: int | None = None
    temperature: float | None = None  # Celsius
    spo2: int | None = None  # Percentage
    respiratory_rate: int | None = None
    weight: float | None = None  # kg
    height: float | None = None  # cm
    bmi: float | None = None
    blood_sugar: float | None = None  # mg/dL
    notes: str = ""


class Allergy(FirestoreDocument, TimestampMixin):
    """Patient allergy record."""
    patient_id: str
    allergen: str
    severity: AllergySeverity = AllergySeverity.MILD
    reaction: str = ""
    noted_date: date | None = None
    verified: bool = False
    notes: str = ""
