"""
RHOS User Models.

Data models for system users, ASHA workers, and related entities.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import Field

from app.models.common import FirestoreDocument, TimestampMixin, UserRole


class User(FirestoreDocument, TimestampMixin):
    """System user (doctor, nurse, admin)."""

    email: str
    name: str
    role: UserRole = UserRole.DOCTOR
    phone: str = ""
    hospital_id: str = ""
    hospital_name: str = ""
    specialization: str = ""
    license_number: str = ""
    is_active: bool = True
    last_login: datetime | None = None
    avatar_url: str = ""
    # Firebase Auth UID (when using Firebase auth mode)
    firebase_uid: str = ""
    # Hashed password (when using local auth mode)
    hashed_password: str = ""
    patient_id: str = ""


class ASHAWorker(FirestoreDocument, TimestampMixin):
    """Accredited Social Health Activist (ASHA) worker."""

    name: str
    phone: str = ""
    village_id: str
    village_name: str = ""
    district: str = ""
    patients_assigned: int = 0
    active_since: date | None = None
    is_active: bool = True
    training_completed: list[str] = Field(default_factory=list)
    supervisor_id: str = ""


class Hospital(FirestoreDocument):
    """Hospital / Primary Health Center."""

    name: str
    type: str = ""  # PHC, CHC, District Hospital, etc.
    district: str = ""
    state: str = "Rajasthan"
    address: str = ""
    beds: int = 0
    specialties: list[str] = Field(default_factory=list)
    phone: str = ""
    email: str = ""
    lat: float = 0.0
    lng: float = 0.0
    is_active: bool = True


class Village(FirestoreDocument):
    """Village demographic data."""

    name: str
    district: str = ""
    state: str = "Rajasthan"
    population: int = 0
    nearest_hospital_id: str = ""
    nearest_hospital_name: str = ""
    distance_to_hospital_km: float = 0.0
    lat: float = 0.0
    lng: float = 0.0
    pincode: str = ""
