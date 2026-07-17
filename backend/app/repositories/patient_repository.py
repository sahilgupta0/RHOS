"""
RHOS Patient Repository.

Firestore CRUD operations for patient-related collections.
"""

from __future__ import annotations

from typing import Any

from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository):
    """Repository for patient documents."""

    def __init__(self):
        super().__init__("patients")

    async def search_patients(
        self, query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Search patients by name."""
        return await self.search("name", query, limit=limit)

    async def get_by_village(
        self, village_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all patients in a village."""
        return await self.list_all(
            filters=[("village_id", "==", village_id)],
            limit=limit,
        )

    async def get_by_asha_worker(
        self, asha_worker_id: str, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get all patients assigned to an ASHA worker."""
        return await self.list_all(
            filters=[("asha_worker_id", "==", asha_worker_id)],
            limit=limit,
        )


class MedicalHistoryRepository(BaseRepository):
    """Repository for medical history documents."""

    def __init__(self):
        super().__init__("medical_history")

    async def get_by_patient(
        self, patient_id: str
    ) -> list[dict[str, Any]]:
        """Get all medical history for a patient."""
        return await self.list_all(
            filters=[("patient_id", "==", patient_id)],
            order_by="diagnosed_date",
            direction="DESCENDING",
        )


class VitalsRepository(BaseRepository):
    """Repository for vital signs documents."""

    def __init__(self):
        super().__init__("vitals")

    async def get_by_patient(
        self, patient_id: str, limit: int = 50
    ) -> list[dict[str, Any]]:
        """Get vital signs for a patient, most recent first."""
        return await self.list_all(
            filters=[("patient_id", "==", patient_id)],
            order_by="recorded_at",
            direction="DESCENDING",
            limit=limit,
        )

    async def get_by_visit(self, visit_id: str) -> list[dict[str, Any]]:
        """Get vitals recorded during a specific visit."""
        return await self.list_all(
            filters=[("visit_id", "==", visit_id)],
        )


class AllergyRepository(BaseRepository):
    """Repository for allergy documents."""

    def __init__(self):
        super().__init__("allergies")

    async def get_by_patient(self, patient_id: str) -> list[dict[str, Any]]:
        """Get all allergies for a patient."""
        return await self.list_all(
            filters=[("patient_id", "==", patient_id)],
        )
