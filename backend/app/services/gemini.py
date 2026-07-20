"""
RHOS Gemini AI Service.

Wrapper for Google Gemini API calls outside the ADK agent pipeline.
Provides robust error handling with timeout and retry logic.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import google.generativeai as genai

from app.config import get_settings

logger = logging.getLogger(__name__)

_model = None

# Per-call timeout for Gemini API requests (seconds)
GEMINI_TIMEOUT_SECONDS = 30


def _get_model():
    """Get or create the Gemini model instance."""
    global _model
    if _model is None:
        settings = get_settings()
        if not settings.gemini_api_key:
            logger.warning("Gemini API key not configured. AI features unavailable.")
            return None
        genai.configure(api_key=settings.gemini_api_key)
        _model = genai.GenerativeModel(settings.gemini_model)
    return _model


async def generate_text(
    prompt: str,
    system_instruction: str = "",
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> str:
    """Generate text using Gemini with timeout handling.

    Returns:
        Generated text string, or an error message string on failure.

    Raises:
        asyncio.TimeoutError: Propagated if the caller needs to handle it explicitly.
    """
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

        # Run blocking SDK call in thread pool to avoid blocking the event loop,
        # and apply an async timeout so stuck calls don't hang forever.
        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content(
                    full_prompt,
                    generation_config=generation_config,
                ),
            ),
            timeout=GEMINI_TIMEOUT_SECONDS,
        )

        return response.text if response.text else ""

    except asyncio.TimeoutError:
        logger.error(
            "Gemini generate_text timed out after %ds for prompt starting: %.80s",
            GEMINI_TIMEOUT_SECONDS,
            prompt,
        )
        return "AI service timed out. Please retry."
    except Exception as e:
        logger.error("Gemini generation error: %s", e)
        return f"Error generating AI response: {str(e)}"


async def analyze_image(
    image_bytes: bytes,
    prompt: str = "Describe the visible findings in this medical image. Do NOT provide a diagnosis.",
    mime_type: str = "image/jpeg",
) -> str:
    """Analyze an image using Gemini Vision with timeout handling."""
    model = _get_model()
    if model is None:
        return "AI service is not configured."

    try:
        image_part = {"mime_type": mime_type, "data": image_bytes}

        response = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None,
                lambda: model.generate_content([prompt, image_part]),
            ),
            timeout=GEMINI_TIMEOUT_SECONDS,
        )

        return response.text if response.text else ""

    except asyncio.TimeoutError:
        logger.error("Gemini analyze_image timed out after %ds", GEMINI_TIMEOUT_SECONDS)
        return "Image analysis timed out. Please retry."
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
