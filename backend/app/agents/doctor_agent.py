"""
RHOS Doctor Agent.

Generates concise clinical summary for doctor review.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "doctor.md"


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are a clinical documentation assistant. Generate a concise clinical summary. NEVER diagnose."


doctor_agent = LlmAgent(
    name="doctor_agent",
    model=get_settings().gemini_model,
    instruction=_load_prompt(),
    description="Generates a comprehensive clinical summary for the doctor's review.",
    output_key="doctor_output",
)
