"""
RHOS Consultation Endpoints.

Start consultations, chat through agent pipeline, upload images.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agents.conversation_agent import conversation_agent
from app.agents.doctor_agent import doctor_agent
from app.agents.followup_agent import followup_agent
from app.agents.history_agent import history_agent
from app.agents.medicine_agent import medicine_agent
from app.agents.triage_agent import triage_agent
from app.agents.shared_memory import SharedMemory
from app.agents.root_agent import run_clinical_pipeline
from app.dependencies import CurrentUser
from app.repositories.consultation_repository import ConsultationRepository
from app.repositories.patient_repository import (
    AllergyRepository,
    MedicalHistoryRepository,
    PatientRepository,
    VitalsRepository,
)
from app.schemas import (
    ConsultationChatRequest,
    ConsultationChatResponse,
    ConsultationResponse,
    ConsultationStartRequest,
    ConsultationSubmitRequest,
    MedicineCheckRequest,
    MedicineCheckResponse,
    SummaryRequest,
    SummaryResponse,
    TriageRequest,
    TriageResponse,
    VisionAnalysisResponse,
)
from app.services.gemini import analyze_image, generate_text
from app.services.medication import check_drug_interactions

logger = logging.getLogger(__name__)

router = APIRouter()
consultation_repo = ConsultationRepository()
patient_repo = PatientRepository()
history_repo = MedicalHistoryRepository()
vitals_repo = VitalsRepository()
allergy_repo = AllergyRepository()


@router.post("/consultation/start", response_model=ConsultationResponse)
async def start_consultation(
    request: ConsultationStartRequest, current_user: CurrentUser
):
    """Start a new consultation session."""
    try:
        consultation_id = f"consult-{uuid.uuid4().hex[:12]}"
        data = {
            "patient_id": request.patient_id,
            "doctor_id": current_user.id,
            "doctor_name": current_user.name,
            "chief_complaint": request.chief_complaint,
            "language": request.language,
            "status": "active",
            "conversation_history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        await consultation_repo.create(data, doc_id=consultation_id)
        data["id"] = consultation_id
        return ConsultationResponse(**data)
    except Exception as e:
        logger.error("Error starting consultation: %s", e)
        raise HTTPException(status_code=500, detail="Failed to start consultation.")


@router.post(
    "/consultation/{consultation_id}/clear", response_model=ConsultationResponse
)
async def clear_consultation(consultation_id: str, current_user: CurrentUser):
    """Clear conversation history and reset the consultation to start fresh."""
    try:
        consultation = await consultation_repo.get_by_id(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        await consultation_repo.update(
            consultation_id,
            {
                "conversation_history": [],
                "symptoms": [],
                "triage_priority": None,
                "triage_reasoning": "",
                "clinical_summary": "",
                "follow_up_plan": "",
                "status": "active",
                "updated_at": datetime.now().isoformat(),
            },
        )

        consultation["id"] = consultation_id
        consultation["conversation_history"] = []
        consultation["symptoms"] = []
        consultation["triage_priority"] = None
        consultation["triage_reasoning"] = ""
        consultation["clinical_summary"] = ""
        consultation["follow_up_plan"] = ""
        consultation["status"] = "active"
        return ConsultationResponse(**consultation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error clearing consultation: %s", e)
        raise HTTPException(status_code=500, detail="Failed to clear consultation.")


@router.post("/consultation/chat", response_model=ConsultationChatResponse)
async def consultation_chat(
    request: ConsultationChatRequest, current_user: CurrentUser
):
    """
    Chat phase — runs ONLY the Conversation Agent.

    Asks follow-up questions and extracts symptoms from the patient's message.
    The full clinical pipeline is triggered separately via /consultation/submit.
    """
    try:
        consultation = await consultation_repo.get_by_id(request.consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        history = consultation.get("conversation_history", [])
        history.append({"role": "patient", "content": request.message})

        conv_prompt = f"""Patient message: {request.message}

Previous conversation:
{json.dumps(history[-5:], indent=2)}

Chief complaint: {consultation.get('chief_complaint', 'Not specified')}

Ask a focused follow-up question to gather more clinical detail. Extract any symptoms mentioned."""

        conv_response_raw = await generate_text(
            prompt=conv_prompt,
            system_instruction=conversation_agent.instruction,
            temperature=0.5,
        )

        try:
            conv_data = json.loads(
                conv_response_raw.strip().strip("`").strip("json").strip()
            )
        except Exception:
            conv_data = {
                "symptoms": [],
                "chief_complaint": consultation.get("chief_complaint", request.message),
                "response_to_patient": conv_response_raw,
            }

        agent_response = conv_data.get("response_to_patient", conv_response_raw)
        history.append({"role": "assistant", "content": agent_response})

        await consultation_repo.update(
            request.consultation_id,
            {
                "conversation_history": history,
                "symptoms": conv_data.get("symptoms", consultation.get("symptoms", [])),
                "chief_complaint": conv_data.get(
                    "chief_complaint", consultation.get("chief_complaint", "")
                ),
                "updated_at": datetime.now().isoformat(),
            },
        )

        return ConsultationChatResponse(
            consultation_id=request.consultation_id,
            agent_response=agent_response,
            symptoms_extracted=conv_data.get("symptoms", []),
            ready_to_submit=bool(conv_data.get("ready_to_submit", False)),
            agent_pipeline_status={"conversation": "completed"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in consultation chat: %s", e)
        raise HTTPException(status_code=500, detail="Failed to process message.")


@router.post("/consultation/submit", response_model=ConsultationChatResponse)
async def consultation_submit(
    request: ConsultationSubmitRequest, current_user: CurrentUser
):
    """
    Submit phase — runs the full clinical pipeline for patients.

    Triggered when the patient clicks 'Submit for Clinical Review'.
    Runs: History → Triage → Medicine → Doctor → Follow-up agents using SharedMemory.
    """
    try:
        consultation = await consultation_repo.get_by_id(request.consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        patient_id = consultation.get("patient_id")
        conv_symptoms = consultation.get("symptoms", [])
        chief_complaint = consultation.get("chief_complaint", "")
        conversation_history = consultation.get("conversation_history", [])

        # Fetch records from repositories
        history_records = await history_repo.get_by_patient(patient_id)
        allergy_records = await allergy_repo.get_by_patient(patient_id)
        vitals_records = await vitals_repo.get_by_patient(patient_id, limit=5)

        # Initialize shared memory
        memory = SharedMemory(
            chief_complaint=chief_complaint,
            conversation_history=conversation_history,
            symptoms=conv_symptoms,
            vitals=vitals_records,
            allergies=[a.get("allergen", "") for a in allergy_records] if allergy_records else [],
            active_conditions=[h.get("condition", "") for h in history_records] if history_records else [],
            current_medications=[h.get("medications", "") for h in history_records if h.get("medications")] if history_records else []
        )

        # Run clinical pipeline sequentially using SharedMemory
        pipeline_status = await run_clinical_pipeline(memory)

        # Append a final summary message to conversation history
        summary_msg = (
            f"✅ Clinical review complete.\n\n"
            f"**Triage:** {memory.triage_priority or 'MEDIUM'}\n"
            f"**Assessment:** {memory.triage_reasoning}\n\n"
            f"**Clinical Summary:**\n{memory.clinical_summary}\n\n"
            f"**Follow-up Plan:**\n{memory.follow_up_plan}"
        )
        conversation_history.append({"role": "assistant", "content": summary_msg})

        updates = {
            "conversation_history": conversation_history,
            "triage_priority": memory.triage_priority or "MEDIUM",
            "triage_reasoning": memory.triage_reasoning,
            "history_summary": memory.medical_history_summary,
            "clinical_summary": memory.clinical_summary,
            "medication_checks": memory.medication_checks,
            "follow_up_plan": memory.follow_up_plan,
            "status": "submitted",
            "updated_at": datetime.now().isoformat(),
        }

        # Save to MongoDB medical_history collection and append to medical_history.csv
        mh_id = f"MH{uuid.uuid4().hex[:6].upper()}"
        mh_data = {
            "patient_id": patient_id,
            "condition": chief_complaint or "Consultation",
            "diagnosed_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "notes": memory.clinical_summary,
        }
        try:
            await history_repo.create(mh_data, doc_id=mh_id)
        except Exception as e:
            logger.error("Error creating medical history document: %s", e)

        try:
            import csv
            import os

            from app.config import get_settings

            settings = get_settings()
            csv_path = os.path.join(settings.datasets_path, "medical_history.csv")
            if os.path.exists(csv_path):
                with open(csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(
                        [
                            mh_id,
                            patient_id,
                            chief_complaint or "Consultation",
                            datetime.now().strftime("%Y-%m-%d"),
                            "active",
                            memory.clinical_summary.replace("\n", " ")
                            .replace("\r", " ")
                            .replace('"', '""'),
                        ]
                    )
        except Exception as csv_err:
            logger.error("Error appending to medical_history.csv: %s", csv_err)

        await consultation_repo.update(request.consultation_id, updates)

        return ConsultationChatResponse(
            consultation_id=request.consultation_id,
            agent_response=summary_msg,
            symptoms_extracted=conv_symptoms,
            triage_priority=memory.triage_priority or "MEDIUM",
            triage_reasoning=memory.triage_reasoning,
            history_summary=memory.medical_history_summary,
            clinical_summary=memory.clinical_summary,
            medication_checks=memory.medication_checks,
            follow_up_plan=memory.follow_up_plan,
            agent_pipeline_status={
                "conversation": "completed",
                **pipeline_status,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error in consultation submit: %s", e)
        raise HTTPException(status_code=500, detail="Failed to run clinical pipeline.")


@router.post("/consultation/upload", response_model=VisionAnalysisResponse)
async def upload_consultation_image(
    consultation_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: CurrentUser = None,
):
    """Upload a medical image for vision analysis."""
    try:
        contents = await file.read()

        # Analyze with Gemini Vision
        findings = await analyze_image(
            image_bytes=contents,
            mime_type=file.content_type or "image/jpeg",
        )

        # Get existing consultation and append findings to conversation history
        consultation = await consultation_repo.get_by_id(consultation_id)
        if consultation:
            history = consultation.get("conversation_history", [])
            history.append(
                {
                    "role": "system",
                    "content": f"[Image Uploaded: Medical Image Analysis] {findings}",
                }
            )
            vision_results = consultation.get("vision_results", [])
            vision_results.append(
                {
                    "image_url": file.filename or "uploaded_image.jpg",
                    "findings": findings,
                    "description": findings,
                    "created_at": datetime.now().isoformat(),
                }
            )
            await consultation_repo.update(
                consultation_id,
                {
                    "conversation_history": history,
                    "vision_results": vision_results,
                    "updated_at": datetime.now().isoformat(),
                },
            )

        return VisionAnalysisResponse(
            findings=findings,
            description=findings,
            recommendations=[
                "Please consult with the treating physician for clinical correlation."
            ],
            disclaimer="AI-generated image description only. Not a medical diagnosis.",
        )
    except Exception as e:
        logger.error("Error analyzing image: %s", e)
        raise HTTPException(status_code=500, detail="Failed to analyze image.")


@router.post("/triage", response_model=TriageResponse)
async def run_triage(request: TriageRequest, current_user: CurrentUser):
    """Run triage classification on symptoms."""
    try:
        schema_format = (
            '{"priority": "HIGH|MEDIUM|LOW", "reasoning": "...", '
            '"confidence": 0.0-1.0, "recommendations": [...]}'
        )
        prompt = f"""Classify the following case by priority (HIGH, MEDIUM, LOW):

Symptoms: {', '.join(request.symptoms)}
Vitals: {json.dumps(request.vitals)}
Medical History: {', '.join(request.medical_history)}
Age: {request.age or 'Unknown'}
Gender: {request.gender or 'Unknown'}

Respond with JSON: {schema_format}"""

        response = await generate_text(
            prompt=prompt,
            system_instruction=(
                "You are a clinical triage assistant. Classify urgency. "
                "Always err on higher priority when uncertain."
            ),
            temperature=0.3,
        )

        # Parse response
        try:
            result = json.loads(response.strip().strip("`").strip())
            if result.get("priority") not in ("HIGH", "MEDIUM", "LOW"):
                result["priority"] = "MEDIUM"
        except (json.JSONDecodeError, AttributeError):
            result = {"priority": "MEDIUM", "reasoning": response, "confidence": 0.5}

        return TriageResponse(
            priority=result.get("priority", "MEDIUM"),
            reasoning=result.get("reasoning", ""),
            confidence=result.get("confidence", 0.5),
            recommendations=result.get("recommendations", []),
        )
    except Exception as e:
        logger.error("Triage error: %s", e)
        raise HTTPException(status_code=500, detail="Triage classification failed.")


@router.post("/medicine/check", response_model=MedicineCheckResponse)
async def check_medication_safety(
    request: MedicineCheckRequest, current_user: CurrentUser
):
    """Check medication safety — interactions, allergies, alternatives."""
    try:
        result = await check_drug_interactions(
            medications=request.medications,
            patient_allergies=request.allergies,
            patient_conditions=request.conditions,
            patient_age=request.age,
        )
        return MedicineCheckResponse(**result)
    except Exception as e:
        logger.error("Medication check error: %s", e)
        raise HTTPException(status_code=500, detail="Medication check failed.")


@router.post("/summary", response_model=SummaryResponse)
async def generate_summary(request: SummaryRequest, current_user: CurrentUser):
    """Generate a clinical summary for a consultation."""
    try:
        consultation = await consultation_repo.get_by_id(request.consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        prompt = f"""Generate a concise clinical summary for this consultation:

Chief Complaint: {consultation.get('chief_complaint', 'N/A')}
Conversation: {json.dumps(consultation.get('conversation_history', [])[-10:])}
Triage: {consultation.get('triage_priority', 'Not assessed')}

Respond with JSON: {{"summary": "...", "assessment": "...", "plan": "...", "follow_up": "..."}}"""

        response = await generate_text(
            prompt=prompt,
            system_instruction=(
                "You are a clinical documentation assistant. "
                "Generate a concise summary. NEVER diagnose."
            ),
            temperature=0.5,
        )

        try:
            result = json.loads(response.strip().strip("`").strip())
        except (json.JSONDecodeError, AttributeError):
            result = {"summary": response}

        return SummaryResponse(
            consultation_id=request.consultation_id,
            summary=result.get("summary", ""),
            assessment=result.get("assessment", ""),
            plan=result.get("plan", ""),
            follow_up=result.get("follow_up", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Summary generation error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to generate summary.")


@router.get("/consultation/{consultation_id}", response_model=ConsultationResponse)
async def get_consultation(consultation_id: str, current_user: CurrentUser):
    """Get a single consultation by ID (includes full conversation_history)."""
    try:
        consultation = await consultation_repo.get_by_id(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")
        consultation["id"] = consultation_id
        return ConsultationResponse(**consultation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching consultation: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve consultation.")


@router.get("/consultations", response_model=list[ConsultationResponse])
async def list_consultations(
    current_user: CurrentUser,
    limit: int = 20,
    patient_id: str = "",
):
    """List recent consultations."""
    try:
        if patient_id:
            consultations = await consultation_repo.get_by_patient(
                patient_id, limit=limit
            )
        else:
            consultations = await consultation_repo.get_recent(limit=limit)
        return [ConsultationResponse(**c) for c in consultations]
    except Exception as e:
        logger.error("Error listing consultations: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve consultations.")
