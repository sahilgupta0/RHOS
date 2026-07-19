"""
RHOS Triage Agent.

Classifies patient cases by priority: LOW, MEDIUM, HIGH.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

from app.core.prompt_manager import make_instruction_provider

triage_agent = LlmAgent(
    name="triage_agent",
    model=get_settings().gemini_model,
    instruction=make_instruction_provider("triage_agent"),
    description="Classifies patient priority (LOW/MEDIUM/HIGH) with clinical reasoning.",
    output_key="triage_output",
)
