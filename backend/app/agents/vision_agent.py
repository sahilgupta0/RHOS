"""
RHOS Vision Agent.

Analyzes medical images and describes visible findings.
"""

from __future__ import annotations

import logging
from google.adk.agents import LlmAgent

from app.config import get_settings
from app.core.prompt_manager import make_instruction_provider

logger = logging.getLogger(__name__)

vision_agent = LlmAgent(
    name="vision_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("vision_agent"),
    description="Analyzes uploaded medical images and describes visible findings objectively.",
    output_key="vision_output",
)
