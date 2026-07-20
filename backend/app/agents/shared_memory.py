"""
Shared Memory for RHOS Agents.

Provides a shared workspace/state where agents can read from and write to.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SharedMemory(BaseModel):
    """Shared state container for clinical sub-agents."""
    
    # Input/Initial Context
    chief_complaint: str = ""
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    symptoms: List[str] = Field(default_factory=list)
    
    # Patient Data
    vitals: List[Dict[str, Any]] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    active_conditions: List[str] = Field(default_factory=list)
    current_medications: List[str] = Field(default_factory=list)
    
    # Agent Outputs (to be populated by each agent sequentially)
    medical_history_summary: str = ""
    triage_priority: Optional[str] = None
    triage_reasoning: str = ""
    medication_checks: List[Dict[str, Any]] = Field(default_factory=list)
    clinical_summary: str = ""
    follow_up_plan: str = ""
    vision_findings: str = ""

    def get_history_agent_input(self) -> str:
        """Construct input context for History Agent."""
        return (
            f"Medical history records:\n"
            f"History: {self.active_conditions}\n"
            f"Allergies: {self.allergies}\n"
            f"Recent Vitals: {self.vitals}"
        )

    def get_triage_agent_input(self) -> str:
        """Construct input context for Triage Agent."""
        return (
            f"Classify the triage priority (LOW, MEDIUM, HIGH) for the patient case:\n"
            f"Chief Complaint: {self.chief_complaint}\n"
            f"Symptoms: {self.symptoms}\n"
            f"Vitals: {self.vitals}\n"
            f"Medical History Summary: {self.medical_history_summary}"
        )

    def get_medicine_agent_input(self) -> str:
        """Construct input context for Medicine Agent."""
        conversation_text = " ".join(
            m["content"] for m in self.conversation_history if m.get("role") == "patient"
        )
        return (
            f"Verify safety and check for drug conflicts/allergies:\n"
            f"Conversation: {conversation_text}\n"
            f"Current Medications: {self.current_medications}\n"
            f"Allergies: {self.allergies}\n"
            f"Conditions: {self.active_conditions}"
        )

    def get_doctor_agent_input(self) -> str:
        """Construct input context for Doctor Agent."""
        return (
            f"Generate clinical note draft (SOAP format):\n"
            f"Chief Complaint: {self.chief_complaint}\n"
            f"Symptoms: {self.symptoms}\n"
            f"Triage Assessment: Priority={self.triage_priority}, Reasoning={self.triage_reasoning}\n"
            f"Medical History: {self.medical_history_summary}\n"
            f"Medication Review: {self.medication_checks}"
        )

    def get_followup_agent_input(self) -> str:
        """Construct input context for Follow-up Agent."""
        return (
            f"Generate care coordination & follow-up recommendations:\n"
            f"Clinical summary: {self.clinical_summary}\n"
            f"Triage: Priority={self.triage_priority}, Reasoning={self.triage_reasoning}"
        )
