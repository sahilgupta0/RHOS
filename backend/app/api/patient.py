"""
RHOS Patient Endpoints.

Patient CRUD, search, and medical history retrieval.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies import CurrentUser
from app.repositories.patient_repository import (
    AllergyRepository,
    MedicalHistoryRepository,
    PatientRepository,
    VitalsRepository,
)
from app.schemas import (
    PatientCreate,
    PatientListResponse,
    PatientResponse,
    PatientUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter()

patient_repo = PatientRepository()
history_repo = MedicalHistoryRepository()
vitals_repo = VitalsRepository()
allergy_repo = AllergyRepository()


@router.get("/patients", response_model=PatientListResponse)
async def list_patients(
    current_user: CurrentUser,
    search: str = Query("", description="Search by patient name"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    village_id: str = Query("", description="Filter by village"),
):
    """List patients with search, filter, and pagination."""
    try:
        offset = (page - 1) * page_size

        if search:
            patients = await patient_repo.search_patients(search, limit=page_size)
        elif village_id:
            patients = await patient_repo.get_by_village(village_id, limit=page_size)
        else:
            patients = await patient_repo.list_all(
                limit=page_size,
                offset=offset,
                order_by="name",
            )

        total = await patient_repo.count()

        return PatientListResponse(
            patients=[PatientResponse(**p) for p in patients],
            total=total,
            page=page,
            page_size=page_size,
        )
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable.")
    except Exception as e:
        logger.error("Error listing patients: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve patients.")


@router.get("/patient/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: str, current_user: CurrentUser):
    """Get patient details by ID."""
    try:
        patient = await patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found.")
        return PatientResponse(**patient)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting patient %s: %s", patient_id, e)
        raise HTTPException(status_code=500, detail="Failed to retrieve patient.")


@router.post(
    "/patient", response_model=PatientResponse, status_code=status.HTTP_201_CREATED
)
async def create_patient(patient: PatientCreate, current_user: CurrentUser):
    """Create a new patient record."""
    try:
        data = patient.model_dump(mode="json")
        data["created_at"] = datetime.now().isoformat()
        data["updated_at"] = datetime.now().isoformat()
        data["is_active"] = True

        doc_id = await patient_repo.create(data)
        data["id"] = doc_id
        return PatientResponse(**data)
    except Exception as e:
        logger.error("Error creating patient: %s", e)
        raise HTTPException(status_code=500, detail="Failed to create patient.")


@router.put("/patient/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str, update: PatientUpdate, current_user: CurrentUser
):
    """Update patient details."""
    try:
        existing = await patient_repo.get_by_id(patient_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Patient not found.")

        update_data = update.model_dump(exclude_none=True, mode="json")
        update_data["updated_at"] = datetime.now().isoformat()
        await patient_repo.update(patient_id, update_data)

        existing.update(update_data)
        return PatientResponse(**existing)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating patient %s: %s", patient_id, e)
        raise HTTPException(status_code=500, detail="Failed to update patient.")


@router.get("/patient/history/{patient_id}")
async def get_patient_history(patient_id: str, current_user: CurrentUser):
    """Get complete medical history for a patient."""
    try:
        patient = await patient_repo.get_by_id(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found.")

        history = await history_repo.get_by_patient(patient_id)
        vitals = await vitals_repo.get_by_patient(patient_id, limit=20)
        allergies = await allergy_repo.get_by_patient(patient_id)

        return {
            "patient": PatientResponse(**patient),
            "medical_history": history,
            "vitals": vitals,
            "allergies": allergies,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting history for patient %s: %s", patient_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve patient history."
        )
