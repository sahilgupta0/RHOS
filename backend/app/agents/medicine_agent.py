"""
RHOS Medicine Agent.

Checks drug interactions, allergy conflicts, and suggests alternatives.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

from app.core.prompt_manager import make_instruction_provider

medicine_agent = LlmAgent(
    name="medicine_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("medicine_agent"),
    description="Checks drug interactions, allergy conflicts, warnings, and suggests generic alternatives.",
    output_key="medicine_output",
)
