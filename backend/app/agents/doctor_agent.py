"""
RHOS Doctor Agent.

Generates concise clinical summary for doctor review.
"""

from __future__ import annotations

import logging
from google.adk.agents import LlmAgent

from app.config import get_settings
from app.core.prompt_manager import make_instruction_provider

logger = logging.getLogger(__name__)

doctor_agent = LlmAgent(
    name="doctor_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("doctor_agent"),
    description="Generates a comprehensive clinical summary for the doctor's review.",
    output_key="doctor_output",
)
