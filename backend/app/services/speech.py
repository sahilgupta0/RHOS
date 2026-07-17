"""
RHOS Speech Service.

Speech-to-text and text-to-speech integration.
Uses Google Cloud Speech API when enabled, with browser fallback.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


async def speech_to_text(
    audio_bytes: bytes,
    language: str = "en-IN",
    encoding: str = "WEBM_OPUS",
    sample_rate: int = 48000,
) -> dict[str, Any]:
    """
    Convert speech audio to text.

    Uses Google Cloud Speech-to-Text API when enabled,
    otherwise returns a message suggesting browser-native STT.
    """
    settings = get_settings()

    if not settings.google_speech_enabled:
        return {
            "text": "",
            "confidence": 0.0,
            "language": language,
            "error": "Server-side STT is not enabled. Use browser Web Speech API.",
            "use_browser_stt": True,
        }

    try:
        from google.cloud import speech

        client = speech.SpeechClient()

        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=getattr(speech.RecognitionConfig.AudioEncoding, encoding, speech.RecognitionConfig.AudioEncoding.WEBM_OPUS),
            sample_rate_hertz=sample_rate,
            language_code=language,
            alternative_language_codes=["hi-IN", "en-US"],
            enable_automatic_punctuation=True,
            model="latest_long",
        )

        response = client.recognize(config=config, audio=audio)

        if response.results:
            best = response.results[0].alternatives[0]
            return {
                "text": best.transcript,
                "confidence": best.confidence,
                "language": language,
            }

        return {"text": "", "confidence": 0.0, "language": language}

    except ImportError:
        logger.warning("google-cloud-speech not installed.")
        return {"text": "", "confidence": 0.0, "error": "Speech library not available."}
    except Exception as e:
        logger.error("Speech-to-text error: %s", e)
        return {"text": "", "confidence": 0.0, "error": str(e)}


async def text_to_speech(
    text: str,
    language: str = "en-IN",
    voice: str = "en-IN-Standard-A",
) -> bytes | None:
    """
    Convert text to speech audio.

    Uses Google Cloud Text-to-Speech API when enabled.
    Returns audio bytes (MP3) or None.
    """
    settings = get_settings()

    if not settings.google_tts_enabled:
        return None

    try:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_config = texttospeech.VoiceSelectionParams(
            language_code=language,
            name=voice,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_config,
            audio_config=audio_config,
        )

        return response.audio_content

    except ImportError:
        logger.warning("google-cloud-texttospeech not installed.")
        return None
    except Exception as e:
        logger.error("Text-to-speech error: %s", e)
        return None
