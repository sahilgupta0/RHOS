"""
RHOS Follow-up Agent.

Generates follow-up plans and recommendations.
"""

from __future__ import annotations

import logging

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

from app.core.prompt_manager import make_instruction_provider

followup_agent = LlmAgent(
    name="followup_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("followup_agent"),
    description="Generates follow-up plans, monitoring instructions, and scheduling recommendations.",
    output_key="followup_output",
)
