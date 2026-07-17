"""
RHOS Common Models.

Base models, enums, and shared types used across the application.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────────────────


class TriagePriority(str, Enum):
    """Triage priority classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Gender(str, Enum):
    """Patient gender."""
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class BloodGroup(str, Enum):
    """Blood group types."""
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class VisitType(str, Enum):
    """Type of patient visit."""
    WALK_IN = "walk-in"
    APPOINTMENT = "appointment"
    FOLLOW_UP = "follow-up"
    EMERGENCY = "emergency"
    REFERRAL = "referral"


class AppointmentStatus(str, Enum):
    """Appointment status."""
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"


class ReferralUrgency(str, Enum):
    """Referral urgency level."""
    ROUTINE = "routine"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class AllergySeverity(str, Enum):
    """Allergy severity level."""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class MedicalConditionStatus(str, Enum):
    """Status of a medical condition."""
    ACTIVE = "active"
    RESOLVED = "resolved"
    CHRONIC = "chronic"
    MANAGED = "managed"


class UserRole(str, Enum):
    """User roles in the system."""
    DOCTOR = "doctor"
    NURSE = "nurse"
    ASHA_WORKER = "asha_worker"
    ADMIN = "admin"
    PATIENT = "patient"


# ── Base Models ────────────────────────────────────────────────────────────────


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class MongoDocument(BaseModel):
    """Base model for MongoDB documents with ID."""
    id: str = ""

    def to_mongo(self) -> dict[str, Any]:
        """Convert model to MongoDB-compatible dict (excludes id)."""
        return self.model_dump(exclude={"id"}, mode="json")

    @classmethod
    def from_mongo(cls, doc_id: str, data: dict[str, Any]) -> MongoDocument:
        """Create model instance from MongoDB document data."""
        return cls(id=doc_id, **data)


# For backwards compatibility with models subclassing FirestoreDocument
class FirestoreDocument(MongoDocument):
    """Deprecated: Use MongoDocument instead."""

    def to_firestore(self) -> dict[str, Any]:
        return self.to_mongo()

    @classmethod
    def from_firestore(cls, doc_id: str, data: dict[str, Any]) -> FirestoreDocument:
        return cls.from_mongo(doc_id, data)
