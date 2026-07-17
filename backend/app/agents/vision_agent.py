"""
RHOS Vision Agent.

Analyzes medical images and describes visible findings.
"""

from __future__ import annotations

import logging
from pathlib import Path

from google.adk.agents import LlmAgent

from app.config import get_settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "vision.md"


def _load_prompt() -> str:
    try:
        return PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "You are a medical image description assistant. Describe visible findings objectively. NEVER diagnose."


vision_agent = LlmAgent(
    name="vision_agent",
    model=get_settings().gemini_model,
    instruction=_load_prompt(),
    description="Analyzes uploaded medical images and describes visible findings objectively.",
    output_key="vision_output",
)
