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

from app.core.prompt_manager import make_instruction_provider

conversation_agent = LlmAgent(
    name="conversation_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("conversation_agent"),
    description="Extracts symptoms, duration, severity, and body location from patient conversation.",
    output_key="conversation_output",
)
