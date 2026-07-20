"""
RHOS Root Agent — Sequential Agent Orchestrator.

Orchestrates all sub-agents in sequence using Google ADK SequentialAgent.
Each agent writes to session state via output_key, and subsequent agents
read from that shared state.
"""

from __future__ import annotations

import json
import logging

from google.adk.agents import SequentialAgent

from app.agents.conversation_agent import conversation_agent
from app.agents.doctor_agent import doctor_agent
from app.agents.followup_agent import followup_agent
from app.agents.history_agent import history_agent
from app.agents.medicine_agent import medicine_agent
from app.agents.triage_agent import triage_agent
from app.agents.shared_memory import SharedMemory
from app.services.gemini import generate_text

logger = logging.getLogger(__name__)

# The root agent orchestrates all sub-agents sequentially.
# Vision agent is excluded from the default pipeline — it's invoked
# on-demand only when images are uploaded.
root_agent = SequentialAgent(
    name="rhos_root_agent",
    description=(
        "RHOS Clinical Decision Support Pipeline. "
        "Orchestrates conversation analysis, history review, triage classification, "
        "medication safety, clinical summary, and follow-up planning."
    ),
    sub_agents=[
        conversation_agent,
        history_agent,
        triage_agent,
        medicine_agent,
        doctor_agent,
        followup_agent,
    ],
)


async def run_clinical_pipeline(memory: SharedMemory) -> dict[str, str]:
    """
    Executes the clinical agent pipeline sequentially using SharedMemory.
    
    Each agent reads its required inputs from the SharedMemory object,
    queries Gemini, and updates the SharedMemory object with its results.
    """
    pipeline_status: dict[str, str] = {}

    # 1. History Agent
    try:
        history_input = memory.get_history_agent_input()
        hist_response_raw = await generate_text(
            prompt=history_input,
            system_instruction=history_agent.instruction,
            temperature=0.3,
        )
        try:
            hist_data = json.loads(
                hist_response_raw.strip().strip("`").strip("json").strip()
            )
        except Exception:
            hist_data = {
                "summary": hist_response_raw,
                "active_conditions": [],
                "current_medications": [],
                "allergies": [],
                "risk_factors": [],
                "clinical_alerts": [],
            }
        
        memory.medical_history_summary = hist_data.get("summary", hist_response_raw)
        memory.active_conditions = hist_data.get("active_conditions", memory.active_conditions)
        memory.current_medications = hist_data.get("current_medications", memory.current_medications)
        memory.allergies = hist_data.get("allergies", memory.allergies)
        pipeline_status["history"] = "completed"
    except Exception as e:
        logger.error("SharedMemory History agent failed: %s", e)
        pipeline_status["history"] = "failed"

    # 2. Triage Agent
    try:
        triage_input = memory.get_triage_agent_input()
        triage_response_raw = await generate_text(
            prompt=triage_input,
            system_instruction=triage_agent.instruction,
            temperature=0.3,
        )
        try:
            triage_data = json.loads(
                triage_response_raw.strip().strip("`").strip("json").strip()
            )
        except Exception:
            triage_data = {
                "priority": "MEDIUM",
                "reasoning": triage_response_raw,
                "confidence": 0.5,
                "recommendations": [],
            }
        
        memory.triage_priority = triage_data.get("priority", "MEDIUM")
        memory.triage_reasoning = triage_data.get("reasoning", triage_response_raw)
        pipeline_status["triage"] = "completed"
    except Exception as e:
        logger.error("SharedMemory Triage agent failed: %s", e)
        pipeline_status["triage"] = "failed"

    # 3. Medicine Agent
    try:
        medicine_input = memory.get_medicine_agent_input()
        med_response_raw = await generate_text(
            prompt=medicine_input,
            system_instruction=medicine_agent.instruction,
            temperature=0.3,
        )
        try:
            med_data = json.loads(
                med_response_raw.strip().strip("`").strip("json").strip()
            )
        except Exception:
            med_data = {
                "interactions": [],
                "allergy_warnings": [],
                "warnings": [med_response_raw] if med_response_raw else [],
                "safe_to_prescribe": True,
            }
        
        memory.medication_checks = (
            med_data.get("interactions", [])
            + med_data.get("allergy_warnings", [])
            + [{"warning": w} for w in med_data.get("warnings", [])]
        )
        pipeline_status["medicine"] = "completed"
    except Exception as e:
        logger.error("SharedMemory Medicine agent failed: %s", e)
        pipeline_status["medicine"] = "failed"

    # 4. Doctor Agent
    try:
        doctor_input = memory.get_doctor_agent_input()
        doc_response_raw = await generate_text(
            prompt=doctor_input,
            system_instruction=doctor_agent.instruction,
            temperature=0.5,
        )
        memory.clinical_summary = doc_response_raw
        pipeline_status["doctor"] = "completed"
    except Exception as e:
        logger.error("SharedMemory Doctor agent failed: %s", e)
        memory.clinical_summary = "Clinical note could not be generated."
        pipeline_status["doctor"] = "failed"

    # 5. Follow-up Agent
    try:
        followup_input = memory.get_followup_agent_input()
        followup_response_raw = await generate_text(
            prompt=followup_input,
            system_instruction=followup_agent.instruction,
            temperature=0.5,
        )
        try:
            followup_data = json.loads(
                followup_response_raw.strip().strip("`").strip("json").strip()
            )
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
        
        memory.follow_up_plan = followup_data.get("patient_education", followup_response_raw)
        pipeline_status["followup"] = "completed"
    except Exception as e:
        logger.error("SharedMemory Follow-up agent failed: %s", e)
        pipeline_status["followup"] = "failed"

    return pipeline_status

