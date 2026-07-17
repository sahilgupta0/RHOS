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

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "triage.md"


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are a clinical triage assistant. Classify patient priority as LOW, MEDIUM, or HIGH."


triage_agent = LlmAgent(
    name="triage_agent",
    model=get_settings().gemini_model,
    instruction=_load_prompt(),
    description="Classifies patient priority (LOW/MEDIUM/HIGH) with clinical reasoning.",
    output_key="triage_output",
)
