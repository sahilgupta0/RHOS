"""
RHOS Speech Endpoints.

Speech-to-text and text-to-speech conversion.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from app.dependencies import CurrentUser
from app.schemas import SpeechToTextResponse, TextToSpeechRequest
from app.services.speech import speech_to_text, text_to_speech

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/speech-to-text", response_model=SpeechToTextResponse)
async def convert_speech_to_text(
    audio: UploadFile = File(...),
    language: str = "en-IN",
    current_user: CurrentUser = None,
):
    """Convert audio to text using Google Speech-to-Text or browser fallback."""
    try:
        audio_bytes = await audio.read()
        result = await speech_to_text(audio_bytes, language=language)
        return SpeechToTextResponse(**result)
    except Exception as e:
        logger.error("Speech-to-text error: %s", e)
        raise HTTPException(status_code=500, detail="Speech-to-text conversion failed.")


@router.post("/text-to-speech")
async def convert_text_to_speech(
    request: TextToSpeechRequest, current_user: CurrentUser = None
):
    """Convert text to speech audio."""
    try:
        audio_bytes = await text_to_speech(
            text=request.text,
            language=request.language,
        )
        if audio_bytes:
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=speech.mp3"},
            )
        else:
            return {
                "message": "Server-side TTS not available. Use browser SpeechSynthesis.",
                "use_browser_tts": True,
            }
    except Exception as e:
        logger.error("Text-to-speech error: %s", e)
        raise HTTPException(status_code=500, detail="Text-to-speech conversion failed.")
