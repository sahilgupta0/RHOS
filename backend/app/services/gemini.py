"""
RHOS Gemini AI Service.

Wrapper for Google Gemini API calls outside the ADK agent pipeline.
"""

from __future__ import annotations

import logging
from typing import Any

import google.generativeai as genai

from app.config import get_settings

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    """Get or create the Gemini model instance."""
    global _model
    if _model is None:
        settings = get_settings()
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured. AI features unavailable.")
            return None
        print("\n\n\nGemini API key: ", settings.gemini_api_key)
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(settings.gemini_model)
        print("Gemini model: ", _model)
    return _model


async def generate_text(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Generate text using Gemini."""
    model = _get_model()
    if model is None:
        return "AI service is not configured. Please set GEMINI_API_KEY."

    try:
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        full_prompt = (
            f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
        )

        print("\n\n\nFull prompt: ", full_prompt)
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config,
        )

        print("\n\n\nResponse: ", response)

        return response.text if response.text else ""
    except Exception as e:
        logger.error("Gemini generation error: %s", e)
        return f"Error generating AI response: {str(e)}"


async def analyze_image(
    image_bytes: bytes,
    prompt: str = "Describe the visible findings in this medical image. Do NOT provide a diagnosis.",
    mime_type: str = "image/jpeg",
) -> str:
    """Analyze an image using Gemini Vision."""
    model = _get_model()
    if model is None:
        return "AI service is not configured."

    try:
        image_part = {"mime_type": mime_type, "data": image_bytes}
        response = model.generate_content([prompt, image_part])
        return response.text if response.text else ""
    except Exception as e:
        logger.error("Gemini vision error: %s", e)
        return f"Error analyzing image: {str(e)}"


async def check_medications(
    medications: list[str],
    allergies: list[str] | None = None,
    conditions: list[str] | None = None,
) -> dict[str, Any]:
    """Check medication safety using Gemini."""
    prompt = f"""You are a clinical pharmacology assistant. Analyze the following medications for safety.

Medications: {', '.join(medications)}
Known Allergies: {', '.join(allergies or ['None reported'])}
Existing Conditions: {', '.join(conditions or ['None reported'])}

Provide your analysis as JSON with these fields:
- interactions: list of {{drug1, drug2, severity, description}}
- allergy_warnings: list of {{medication, allergen, risk_level}}
- warnings: list of general warning strings
- alternatives: list of {{medication, alternative, reason}}
- safe_to_prescribe: boolean

IMPORTANT: This is for clinical decision SUPPORT only. Always recommend pharmacist verification.
Respond with valid JSON only."""

    response = await generate_text(prompt, temperature=0.3)

    # Try to parse JSON response
    try:
        import json

        # Extract JSON from response if wrapped in markdown
        json_str = response.strip()
        if json_str.startswith("```"):
            json_str = json_str.split("\n", 1)[1].rsplit("```", 1)[0]
        return json.loads(json_str)
    except (json.JSONDecodeError, IndexError):
        return {
            "interactions": [],
            "allergy_warnings": [],
            "warnings": [response],
            "alternatives": [],
            "safe_to_prescribe": True,
        }
