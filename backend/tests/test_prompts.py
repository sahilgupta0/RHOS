import pytest

from app.core.prompt_manager import prompt_manager


@pytest.mark.asyncio
async def test_prompt_manager_sync_fallback():
    """Test PromptManager sync fallback to default file or hardcoded default."""
    prompt_manager.clear_cache()

    # 1. Test a valid agent prompt
    prompt = prompt_manager.get_prompt_sync("conversation_agent")
    assert prompt is not None
    assert "intake" in prompt.lower() or "symptoms" in prompt.lower()

    # 2. Test an unknown agent prompt fallback
    prompt_unknown = prompt_manager.get_prompt_sync("non_existent_agent")
    assert prompt_unknown == "You are a helpful clinical assistant."


@pytest.mark.asyncio
async def test_prompt_manager_db_override(mock_db_setup):
    """Test PromptManager database override behavior."""
    prompt_manager.clear_cache()

    # Pre-populate prompts collection in mock db
    mock_db_setup["prompts"] = {
        "conversation_agent": {
            "_id": "conversation_agent",
            "text": "Custom Conversation Prompt override instruction",
        }
    }

    # Fetch prompt asynchronously - should return database override
    prompt = await prompt_manager.get_prompt("conversation_agent")
    assert prompt == "Custom Conversation Prompt override instruction"

    # Reset prompt should delete the override
    await prompt_manager.reset_prompt("conversation_agent")
    assert "conversation_agent" not in mock_db_setup["prompts"]

    # Now it should fallback to file/cache
    prompt_fallback = await prompt_manager.get_prompt("conversation_agent")
    assert "intake" in prompt_fallback.lower() or "symptoms" in prompt_fallback.lower()


@pytest.mark.asyncio
async def test_prompt_manager_set_prompt(mock_db_setup):
    """Test PromptManager set_prompt updates mock database."""
    prompt_manager.clear_cache()

    if "prompts" not in mock_db_setup:
        mock_db_setup["prompts"] = {}

    await prompt_manager.set_prompt("triage_agent", "Custom triage rules")

    assert "triage_agent" in mock_db_setup["prompts"]
    assert mock_db_setup["prompts"]["triage_agent"]["text"] == "Custom triage rules"

    # Get prompt should return new value
    prompt = await prompt_manager.get_prompt("triage_agent")
    assert prompt == "Custom triage rules"
