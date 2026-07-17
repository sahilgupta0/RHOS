"""
RHOS Conversation Agent.

Extracts symptoms, duration, severity from patient conversation.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "conversation.md"


def _load_prompt() -> str:
    """Load the conversation agent prompt from file."""
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Conversation prompt file not found at %s", PROMPT_PATH)
        return "You are a clinical intake assistant. Extract symptoms from the patient conversation as structured JSON."


conversation_agent = LlmAgent(
    name="conversation_agent",
    model=get_settings().gemini_model,
    instruction=_load_prompt(),
    description="Extracts symptoms, duration, severity, and body location from patient conversation.",
    output_key="conversation_output",
)
