"""
RHOS Consultation Endpoints.

Start consultations, chat through agent pipeline, upload images.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from app.dependencies import CurrentUser
from app.repositories.consultation_repository import ConsultationRepository
from app.repositories.patient_repository import (
    PatientRepository,
    MedicalHistoryRepository,
    VitalsRepository,
    AllergyRepository,
)
from app.agents.conversation_agent import conversation_agent
from app.agents.history_agent import history_agent
from app.agents.triage_agent import triage_agent
from app.agents.medicine_agent import medicine_agent
from app.agents.doctor_agent import doctor_agent
from app.agents.followup_agent import followup_agent

from app.schemas import (
    ConsultationChatRequest,
    ConsultationChatResponse,
    ConsultationSubmitRequest,
    ConsultationResponse,
    ConsultationStartRequest,
    MedicineCheckRequest,
    MedicineCheckResponse,
    SummaryRequest,
    SummaryResponse,
    TriageRequest,
    TriageResponse,
    VisionAnalysisResponse,
)
from app.services.gemini import generate_text, analyze_image
from app.services.medication import check_drug_interactions

logger = logging.getLogger(__name__)

router = APIRouter()
consultation_repo = ConsultationRepository()
patient_repo = PatientRepository()
history_repo = MedicalHistoryRepository()
vitals_repo = VitalsRepository()
allergy_repo = AllergyRepository()


@router.post("/consultation/start", response_model=ConsultationResponse)
async def start_consultation(request: ConsultationStartRequest, current_user: CurrentUser):
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


@router.post("/consultation/{consultation_id}/clear", response_model=ConsultationResponse)
async def clear_consultation(consultation_id: str, current_user: CurrentUser):
    """Clear conversation history and reset the consultation to start fresh."""
    try:
        consultation = await consultation_repo.get_by_id(consultation_id)
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        await consultation_repo.update(consultation_id, {
            "conversation_history": [],
            "symptoms": [],
            "triage_priority": None,
            "triage_reasoning": "",
            "clinical_summary": "",
            "follow_up_plan": "",
            "status": "active",
            "updated_at": datetime.now().isoformat(),
        })

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
async def consultation_chat(request: ConsultationChatRequest, current_user: CurrentUser):
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
            conv_data = json.loads(conv_response_raw.strip().strip("`").strip("json").strip())
        except Exception:
            conv_data = {
                "symptoms": [],
                "chief_complaint": consultation.get("chief_complaint", request.message),
                "response_to_patient": conv_response_raw,
            }

        agent_response = conv_data.get("response_to_patient", conv_response_raw)
        history.append({"role": "assistant", "content": agent_response})

        await consultation_repo.update(request.consultation_id, {
            "conversation_history": history,
            "symptoms": conv_data.get("symptoms", consultation.get("symptoms", [])),
            "chief_complaint": conv_data.get("chief_complaint", consultation.get("chief_complaint", "")),
            "updated_at": datetime.now().isoformat(),
        })

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
async def consultation_submit(request: ConsultationSubmitRequest, current_user: CurrentUser):
    """
    Submit phase — runs the full clinical pipeline for patients.

    Triggered when the patient clicks 'Submit for Clinical Review'.
    Runs: History → Triage → Medicine → Doctor → Follow-up agents.
    """
    try:
        consultation = await consultation_repo.get_by_id(request.consultation_id)

        print(f"\n\n\nConsultation_id: {request.consultation_id}\n\n\n")
        print(f"\n\n\nConsultation: {consultation}\n\n\n")
        if not consultation:
            raise HTTPException(status_code=404, detail="Consultation not found.")

        patient_id = consultation.get("patient_id")
        conv_symptoms = consultation.get("symptoms", [])
        chief_complaint = consultation.get("chief_complaint", "")
        conversation_history = consultation.get("conversation_history", [])

        # 1. History Agent
        history_records = await history_repo.get_by_patient(patient_id)
        allergy_records = await allergy_repo.get_by_patient(patient_id)
        vitals_records = await vitals_repo.get_by_patient(patient_id, limit=5)

        history_prompt = f"""Medical history records:
History: {json.dumps(history_records, indent=2)}
Allergies: {json.dumps(allergy_records, indent=2)}
Recent Vitals: {json.dumps(vitals_records, indent=2)}"""

        hist_response_raw = await generate_text(
            prompt=history_prompt,
            system_instruction=history_agent.instruction,
            temperature=0.3,
        )
        try:
            hist_data = json.loads(hist_response_raw.strip().strip("`").strip("json").strip())
        except Exception:
            hist_data = {
                "summary": hist_response_raw,
                "active_conditions": [],
                "current_medications": [],
                "allergies": [],
                "risk_factors": [],
                "clinical_alerts": [],
            }

        # 2. Triage Agent
        triage_prompt = f"""Classify the triage priority (LOW, MEDIUM, HIGH) for the patient case:
Chief Complaint: {chief_complaint}
Symptoms: {json.dumps(conv_symptoms)}
Vitals: {json.dumps(vitals_records, indent=2)}
Medical History Summary: {hist_data.get('summary', '')}"""

        triage_response_raw = await generate_text(
            prompt=triage_prompt,
            system_instruction=triage_agent.instruction,
            temperature=0.3,
        )
        try:
            triage_data = json.loads(triage_response_raw.strip().strip("`").strip("json").strip())
        except Exception:
            triage_data = {"priority": "MEDIUM", "reasoning": triage_response_raw, "confidence": 0.5, "recommendations": []}

        # 3. Medicine Agent
        # Build a summary of the conversation for medicine safety check
        conversation_text = " ".join(
            m["content"] for m in conversation_history if m.get("role") == "patient"
        )
        medicine_prompt = f"""Verify safety and check for drug conflicts/allergies:
Conversation: {conversation_text}
Current Medications: {json.dumps(hist_data.get('current_medications', []))}
Allergies: {json.dumps(hist_data.get('allergies', []))}
Conditions: {json.dumps(hist_data.get('active_conditions', []))}"""

        med_response_raw = await generate_text(
            prompt=medicine_prompt,
            system_instruction=medicine_agent.instruction,
            temperature=0.3,
        )
        try:
            med_data = json.loads(med_response_raw.strip().strip("`").strip("json").strip())
        except Exception:
            med_data = {"interactions": [], "allergy_warnings": [], "warnings": [med_response_raw], "safe_to_prescribe": True}

        # 4. Doctor Agent
        doctor_prompt = f"""Generate clinical note draft (SOAP format):
Chief Complaint: {chief_complaint}
Symptoms: {json.dumps(conv_symptoms)}
Triage Assessment: {json.dumps(triage_data)}
Medical History: {json.dumps(hist_data)}
Medication Review: {json.dumps(med_data)}"""

        doc_response_raw = await generate_text(
            prompt=doctor_prompt,
            system_instruction=doctor_agent.instruction,
            temperature=0.5,
        )

        # 5. Follow-up Agent
        followup_prompt = f"""Generate care coordination & follow-up recommendations:
Clinical summary: {doc_response_raw}
Triage: {json.dumps(triage_data)}"""

        followup_response_raw = await generate_text(
            prompt=followup_prompt,
            system_instruction=followup_agent.instruction,
            temperature=0.5,
        )
        try:
            followup_data = json.loads(followup_response_raw.strip().strip("`").strip("json").strip())
        except Exception:
            followup_data = {
                "follow_up_date": "1 week",
                "monitoring_instructions": [],
                "warning_signs": [],
                "lifestyle_recommendations": [],
                "asha_worker_tasks": [],
                "referral_consideration": "none",
                "patient_education": followup_response_raw,
            }

        # Append a final summary message to conversation history
        summary_msg = (
            f"✅ Clinical review complete.\n\n"
            f"**Triage:** {triage_data.get('priority', 'MEDIUM')}\n"
            f"**Assessment:** {triage_data.get('reasoning', '')}\n\n"
            f"**Clinical Summary:**\n{doc_response_raw}\n\n"
            f"**Follow-up Plan:**\n{followup_data.get('patient_education', followup_response_raw)}"
        )
        conversation_history.append({"role": "assistant", "content": summary_msg})

        updates = {
            "conversation_history": conversation_history,
            "triage_priority": triage_data.get("priority", "MEDIUM"),
            "triage_reasoning": triage_data.get("reasoning", ""),
            "history_summary": hist_data.get("summary", ""),
            "clinical_summary": doc_response_raw,
            "medication_checks": (
                med_data.get("interactions", [])
                + med_data.get("allergy_warnings", [])
                + [{"warning": w} for w in med_data.get("warnings", [])]
            ),
            "follow_up_plan": followup_data.get("patient_education", followup_response_raw),
            "status": "submitted",
            "updated_at": datetime.now().isoformat(),
        }
        if "follow_up_date" in followup_data:
            updates["duration"] = followup_data["follow_up_date"]

        # Save to MongoDB medical_history collection and append to medical_history.csv
        mh_id = f"MH{uuid.uuid4().hex[:6].upper()}"
        mh_data = {
            "patient_id": patient_id,
            "condition": chief_complaint or "Consultation",
            "diagnosed_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "notes": doc_response_raw,
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
                    writer.writerow([
                        mh_id,
                        patient_id,
                        chief_complaint or "Consultation",
                        datetime.now().strftime("%Y-%m-%d"),
                        "active",
                        doc_response_raw.replace("\n", " ").replace("\r", " ").replace('"', '""')
                    ])
        except Exception as csv_err:
            logger.error("Error appending to medical_history.csv: %s", csv_err)

        await consultation_repo.update(request.consultation_id, updates)

        return ConsultationChatResponse(
            consultation_id=request.consultation_id,
            agent_response=summary_msg,
            symptoms_extracted=conv_symptoms,
            triage_priority=triage_data.get("priority", "MEDIUM"),
            triage_reasoning=triage_data.get("reasoning", ""),
            history_summary=hist_data.get("summary", ""),
            clinical_summary=doc_response_raw,
            medication_checks=med_data.get("interactions", []) + med_data.get("allergy_warnings", []),
            follow_up_plan=followup_data.get("patient_education", followup_response_raw),
            agent_pipeline_status={
                "conversation": "completed",
                "history": "completed",
                "triage": "completed",
                "medicine": "completed",
                "doctor": "completed",
                "followup": "completed",
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
            history.append({
                "role": "system",
                "content": f"[Image Uploaded: Medical Image Analysis] {findings}"
            })
            vision_results = consultation.get("vision_results", [])
            vision_results.append({
                "image_url": file.filename or "uploaded_image.jpg",
                "findings": findings,
                "description": findings,
                "created_at": datetime.now().isoformat()
            })
            await consultation_repo.update(consultation_id, {
                "conversation_history": history,
                "vision_results": vision_results,
                "updated_at": datetime.now().isoformat()
            })

        return VisionAnalysisResponse(
            findings=findings,
            description=findings,
            recommendations=["Please consult with the treating physician for clinical correlation."],
            disclaimer="AI-generated image description only. Not a medical diagnosis.",
        )
    except Exception as e:
        logger.error("Error analyzing image: %s", e)
        raise HTTPException(status_code=500, detail="Failed to analyze image.")


@router.post("/triage", response_model=TriageResponse)
async def run_triage(request: TriageRequest, current_user: CurrentUser):
    """Run triage classification on symptoms."""
    try:
        prompt = f"""Classify the following case by priority (HIGH, MEDIUM, LOW):

Symptoms: {', '.join(request.symptoms)}
Vitals: {json.dumps(request.vitals)}
Medical History: {', '.join(request.medical_history)}
Age: {request.age or 'Unknown'}
Gender: {request.gender or 'Unknown'}

Respond with JSON: {{"priority": "HIGH|MEDIUM|LOW", "reasoning": "...", "confidence": 0.0-1.0, "recommendations": [...]}}"""

        response = await generate_text(
            prompt=prompt,
            system_instruction="You are a clinical triage assistant. Classify urgency. Always err on higher priority when uncertain.",
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
async def check_medication_safety(request: MedicineCheckRequest, current_user: CurrentUser):
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
            system_instruction="You are a clinical documentation assistant. Generate a concise summary. NEVER diagnose.",
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
            consultations = await consultation_repo.get_by_patient(patient_id, limit=limit)
        else:
            consultations = await consultation_repo.get_recent(limit=limit)
        return [ConsultationResponse(**c) for c in consultations]
    except Exception as e:
        logger.error("Error listing consultations: %s", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve consultations.")
