"""
RHOS Consultation Repository.

Firestore CRUD operations for consultation-related collections.
"""

from __future__ import annotations

from typing import Any

from app.repositories.base_repository import BaseRepository


class ConsultationRepository(BaseRepository):
    """Repository for consultation documents."""

    def __init__(self):
        super().__init__("consultations")

    async def get_by_patient(
        self, patient_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get all consultations for a patient."""
        return await self.list_all(
            filters=[("patient_id", "==", patient_id)],
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )

    async def get_active(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get all active consultations."""
        return await self.list_all(
            filters=[("status", "==", "active")],
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )

    async def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent consultations."""
        return await self.list_all(
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )

    async def get_by_doctor(
        self, doctor_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get consultations by doctor."""
        return await self.list_all(
            filters=[("doctor_id", "==", doctor_id)],
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )

    async def get_by_priority(
        self, priority: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get consultations by triage priority."""
        return await self.list_all(
            filters=[("triage_priority", "==", priority)],
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )


class TriageLogRepository(BaseRepository):
    """Repository for triage log documents."""

    def __init__(self):
        super().__init__("triage_logs")

    async def get_by_consultation(
        self, consultation_id: str
    ) -> list[dict[str, Any]]:
        """Get triage logs for a consultation."""
        return await self.list_all(
            filters=[("consultation_id", "==", consultation_id)],
        )


class DoctorNoteRepository(BaseRepository):
    """Repository for doctor note documents."""

    def __init__(self):
        super().__init__("doctor_notes")

    async def get_by_consultation(
        self, consultation_id: str
    ) -> dict[str, Any] | None:
        """Get doctor note for a consultation."""
        results = await self.list_all(
            filters=[("consultation_id", "==", consultation_id)],
            limit=1,
        )
        return results[0] if results else None

    async def get_by_patient(
        self, patient_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Get all doctor notes for a patient."""
        return await self.list_all(
            filters=[("patient_id", "==", patient_id)],
            order_by="created_at",
            direction="DESCENDING",
            limit=limit,
        )
