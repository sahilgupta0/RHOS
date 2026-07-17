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

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "medicine.md"


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are a clinical pharmacology assistant. Check medications for interactions and safety."


medicine_agent = LlmAgent(
    name="medicine_agent",
    model=get_settings().gemini_model,
    instruction=_load_prompt(),
    description="Checks drug interactions, allergy conflicts, warnings, and suggests generic alternatives.",
    output_key="medicine_output",
)
