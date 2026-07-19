from __future__ import annotations

from unittest.mock import AsyncMock, patch


@patch("app.api.speech.speech_to_text", new_callable=AsyncMock)
def test_speech_to_text_success(mock_stt, client, auth_header):
    """Test speech to text conversion endpoint."""
    mock_stt.return_value = {"text": "Hello Doctor", "confidence": 0.95}

    files = {"audio": ("test.wav", b"audio_content_bytes", "audio/wav")}
    response = client.post(
        "/speech-to-text?language=en-US",
        files=files,
        headers=auth_header,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Hello Doctor"
    assert data["confidence"] == 0.95
    mock_stt.assert_called_once_with(b"audio_content_bytes", language="en-US")


@patch("app.api.speech.speech_to_text", new_callable=AsyncMock)
def test_speech_to_text_failure(mock_stt, client, auth_header):
    """Test speech to text conversion endpoint on service exception."""
    mock_stt.side_effect = Exception("Speech client error")

    files = {"audio": ("test.wav", b"audio_content_bytes", "audio/wav")}
    response = client.post("/speech-to-text", files=files, headers=auth_header)
    assert response.status_code == 500
    assert response.json()["detail"] == "Speech-to-text conversion failed."


@patch("app.api.speech.text_to_speech", new_callable=AsyncMock)
def test_text_to_speech_audio_returned(mock_tts, client, auth_header):
    """Test text to speech endpoint returning audio bytes."""
    mock_tts.return_value = b"mp3_audio_bytes"

    payload = {"text": "Welcome to RHOS", "language": "en-US"}
    response = client.post("/text-to-speech", json=payload, headers=auth_header)
    assert response.status_code == 200
    assert response.content == b"mp3_audio_bytes"
    assert response.headers["content-type"] == "audio/mpeg"


@patch("app.api.speech.text_to_speech", new_callable=AsyncMock)
def test_text_to_speech_fallback_returned(mock_tts, client, auth_header):
    """Test text to speech endpoint returning fallback when TTS fails."""
    mock_tts.return_value = None

    payload = {"text": "Welcome to RHOS", "language": "en-US"}
    response = client.post("/text-to-speech", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["use_browser_tts"] is True
    assert "browser" in data["message"].lower()


@patch("app.api.speech.text_to_speech", new_callable=AsyncMock)
def test_text_to_speech_failure(mock_tts, client, auth_header):
    """Test text to speech endpoint on service error."""
    mock_tts.side_effect = Exception("TTS API error")

    payload = {"text": "Welcome to RHOS", "language": "en-US"}
    response = client.post("/text-to-speech", json=payload, headers=auth_header)
    assert response.status_code == 500
    assert response.json()["detail"] == "Text-to-speech conversion failed."
