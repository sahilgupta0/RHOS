import pytest
from unittest.mock import AsyncMock, patch

from app.agents.shared_memory import SharedMemory
from app.agents.root_agent import run_clinical_pipeline


@pytest.mark.asyncio
async def test_shared_memory_structure():
    """Test that SharedMemory gets initialized and formats prompts correctly."""
    memory = SharedMemory(
        chief_complaint="Severe headache and fever",
        conversation_history=[
            {"role": "patient", "content": "I have had a headache for 2 days."},
            {"role": "assistant", "content": "Any other symptoms?"},
            {"role": "patient", "content": "Yes, high fever."}
        ],
        symptoms=["headache", "fever"],
        vitals=[{"temp": 102}],
        allergies=["penicillin"],
        active_conditions=["hypertension"],
        current_medications=["amlodipine"]
    )
    
    assert memory.chief_complaint == "Severe headache and fever"
    assert "temp" in memory.get_history_agent_input()
    assert "headache" in memory.get_triage_agent_input()
    assert "amlodipine" in memory.get_medicine_agent_input()
    assert "hypertension" in memory.get_history_agent_input()


@pytest.mark.asyncio
@patch("app.agents.root_agent.generate_text", new_callable=AsyncMock)
async def test_run_clinical_pipeline(mock_generate_text):
    """Test run_clinical_pipeline updates shared memory sequentially."""
    # Set up mock responses for each of the 5 agents
    mock_generate_text.side_effect = [
        # 1. History Agent
        '{"summary": "Patient has history of hypertension", "active_conditions": ["hypertension"], "current_medications": ["amlodipine"], "allergies": ["penicillin"]}',
        # 2. Triage Agent
        '{"priority": "HIGH", "reasoning": "High fever and headache might indicate meningitis", "confidence": 0.9}',
        # 3. Medicine Agent
        '{"interactions": [], "allergy_warnings": [{"warning": "watch for skin rash"}], "safe_to_prescribe": true}',
        # 4. Doctor Agent
        "SOAP Clinical Note Draft Content",
        # 5. Follow-up Agent
        '{"patient_education": "Rest and monitor temperature. Follow up in 2 days."}'
    ]

    memory = SharedMemory(
        chief_complaint="Severe headache and fever",
        conversation_history=[{"role": "patient", "content": "headache and fever"}],
        symptoms=["headache", "fever"],
        vitals=[{"temp": 102}],
        allergies=["penicillin"],
        active_conditions=["hypertension"],
        current_medications=["amlodipine"]
    )

    status = await run_clinical_pipeline(memory)

    assert status["history"] == "completed"
    assert status["triage"] == "completed"
    assert status["medicine"] == "completed"
    assert status["doctor"] == "completed"
    assert status["followup"] == "completed"

    assert memory.medical_history_summary == "Patient has history of hypertension"
    assert memory.triage_priority == "HIGH"
    assert "meningitis" in memory.triage_reasoning
    assert memory.clinical_summary == "SOAP Clinical Note Draft Content"
    assert "Rest and monitor temperature" in memory.follow_up_plan
    assert len(memory.medication_checks) > 0
