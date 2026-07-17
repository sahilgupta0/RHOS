"""
RHOS Vision Service.

Handles medical image processing and Gemini Vision analysis.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.gemini import analyze_image as gemini_analyze_image

logger = logging.getLogger(__name__)


async def analyze_medical_image(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> dict[str, Any]:
    """
    Analyze a medical image (skin lesion, wound, eye condition, etc.)
    using Gemini Vision and output descriptive findings.
    """
    prompt = """You are a clinical vision assistant. Describe the visible findings in the provided medical image.
Focus on objective observations such as color, size, shape, borders, texture, and surrounding tissue.

CRITICAL RULES:
1. Do NOT provide a diagnosis or name specific diseases.
2. Do NOT suggest treatments or prescriptions.
3. Be purely descriptive.
4. Output your response as a JSON structure with these fields:
   - description: detailed text description of findings
   - findings: list of objects with fields 'location', 'observation', and 'characteristics' (list of descriptors)
   - confidence: estimate from 0.0 to 1.0
   - recommendations: suggested follow-up observations (e.g. consult clinical specialist)
   - disclaimer: ALWAYS include 'AI-generated description only. Not a medical diagnosis.'
"""

    try:
        response_text = await gemini_analyze_image(
            image_bytes=image_bytes,
            prompt=prompt,
            mime_type=mime_type,
        )

        # Parse JSON from response
        import json
        clean_text = response_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("\n", 1)[1].rsplit("```", 1)[0]

        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Fallback if AI didn't format as JSON
            return {
                "description": response_text,
                "findings": [],
                "confidence": 0.5,
                "recommendations": ["Correlate findings clinically with a medical professional."],
                "disclaimer": "AI-generated description only. Not a medical diagnosis."
            }

    except Exception as e:
        logger.error("Error in vision analysis service: %s", e)
        return {
            "description": f"Failed to analyze image: {str(e)}",
            "findings": [],
            "confidence": 0.0,
            "recommendations": [],
            "disclaimer": "AI vision analysis failed."
        }
