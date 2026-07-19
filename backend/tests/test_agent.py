import pytest
from unittest.mock import MagicMock
from google.adk.agents.readonly_context import ReadonlyContext
from app.core.prompt_manager import make_instruction_provider, prompt_manager
from app.agents.root_agent import root_agent
from app.agents.conversation_agent import conversation_agent

@pytest.mark.asyncio
async def test_agent_instruction_provider():
    """Test that agent instruction provider resolves correctly."""
    prompt_manager.clear_cache()
    provider = make_instruction_provider("conversation_agent")
    
    mock_ctx = MagicMock(spec=ReadonlyContext)
    instruction = await provider(mock_ctx)
    
    assert instruction is not None
    assert "symptoms" in instruction.lower() or "intake" in instruction.lower()


def test_sequential_agent_config():
    """Test root sequential agent sub-agents configuration."""
    assert root_agent.name == "rhos_root_agent"
    assert len(root_agent.sub_agents) == 6
    
    sub_agent_names = [agent.name for agent in root_agent.sub_agents]
    assert "conversation_agent" in sub_agent_names
    assert "doctor_agent" in sub_agent_names
    assert "followup_agent" in sub_agent_names
    assert "history_agent" in sub_agent_names
    assert "medicine_agent" in sub_agent_names
    assert "triage_agent" in sub_agent_names

    # Check that followup agent has dynamic instruction
    assert callable(conversation_agent.instruction)
