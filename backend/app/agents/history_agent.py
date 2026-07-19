"""
RHOS History Agent.

Summarizes patient medical history for clinical reference.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

from app.core.prompt_manager import make_instruction_provider

history_agent = LlmAgent(
    name="history_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("history_agent"),
    description="Summarizes patient medical history: conditions, surgeries, allergies, medications.",
    output_key="history_output",
)
