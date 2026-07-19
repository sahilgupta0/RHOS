from __future__ import annotations

import math
from unittest.mock import AsyncMock, MagicMock, patch, ANY
import pytest

from app.services.maps import calculate_distance_km, get_nearest_hospitals
from app.services.firebase_storage import upload_file, get_storage_bucket
from app.core.firebase_init import get_firestore_client, is_firebase_initialized
from app.services.firestore import get_document, save_document
from app.services.gemini import generate_text, analyze_image
from app.services.speech import speech_to_text, text_to_speech
from app.services.vision import analyze_medical_image
from app.services.medication import check_drug_interactions


# ── Test Maps Service ─────────────────────────────────────────────────────────

def test_calculate_distance_km():
    """Test haversine formula distance calculation."""
    # Distance between Sikar and Jaipur (approx 110-115 km)
    dist = calculate_distance_km(27.6124, 75.1398, 26.9124, 75.7873)
    assert 100 <= dist <= 130


@pytest.mark.asyncio
async def test_get_nearest_hospitals_mock_fallback():
    """Test get nearest hospitals fallback when DB returns empty/none."""
    with patch("app.core.mongodb.get_mongodb_db", return_value=None):
        hospitals = await get_nearest_hospitals(27.6124, 75.1398)
        assert len(hospitals) == 2
        assert hospitals[0]["id"] == "H001"


# ── Test Firebase Storage Service ─────────────────────────────────────────────

def test_get_storage_bucket_not_initialized():
    """Test get storage bucket returns None if Firebase is not initialized."""
    with patch("app.core.firebase_init.is_firebase_initialized", return_value=False):
        assert get_storage_bucket() is None


@pytest.mark.asyncio
async def test_upload_file_not_initialized():
    """Test upload_file raises ConnectionError if storage bucket is not initialized."""
    with patch("app.services.firebase_storage.get_storage_bucket", return_value=None):
        with pytest.raises(ConnectionError, match="Firebase Storage is not initialized"):
            await upload_file(b"content", "test.txt", "text/plain")


@pytest.mark.asyncio
async def test_upload_file_success():
    """Test successful upload_file with mock Firebase bucket."""
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_blob.public_url = "https://storage.googleapis.com/rhos/test.txt"

    with patch("app.services.firebase_storage.get_storage_bucket", return_value=mock_bucket):
        res = await upload_file(b"file_contents", "test.txt", "text/plain")
        assert res["file_url"] == "https://storage.googleapis.com/rhos/test.txt"
        assert res["file_name"].endswith("test.txt")
        mock_bucket.blob.assert_called_once()
        mock_blob.upload_from_string.assert_called_once_with(b"file_contents", content_type="text/plain")


# ── Test Firebase Core / Init ──────────────────────────────────────────────────

def test_firestore_client_checks():
    """Test firestore helper functions."""
    assert is_firebase_initialized() is False
    assert get_firestore_client() is None


# ── Test Firestore Service ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_document_not_initialized():
    """Test get_document returns None if client not initialized."""
    with patch("app.services.firestore.get_firestore_client", return_value=None):
        res = await get_document("patients", "p1")
        assert res is None


@pytest.mark.asyncio
async def test_save_document_not_initialized():
    """Test save_document raises ConnectionError if client not initialized."""
    with patch("app.services.firestore.get_firestore_client", return_value=None):
        with pytest.raises(ConnectionError, match="Firestore client not initialized"):
            await save_document("patients", {"name": "test"})


# ── Test Gemini Service ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_generate_text_gemini_success():
    """Test generate_text returns global mocked result from conftest."""
    res = await generate_text("Hi", "system instruction")
    assert "mocked reasoning" in res


@pytest.mark.asyncio
async def test_analyze_image_gemini_success():
    """Test analyze_image returns global mocked result from conftest."""
    res = await analyze_image(b"fake_image_bytes", "image/png")
    assert res == "Mocked visible image findings."


# ── Test Vision Service ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_analyze_image_vision_helper():
    """Test Vision service helper function delegates to gemini."""
    with patch("app.services.vision.gemini_analyze_image", new_callable=AsyncMock) as mock_gemini:
        mock_gemini.return_value = '{"description": "Mocked findings", "findings": [], "confidence": 0.8}'
        res = await analyze_medical_image(b"image_data", "image/jpeg")
        assert res["description"] == "Mocked findings"
        mock_gemini.assert_called_once_with(
            image_bytes=b"image_data",
            prompt=ANY,
            mime_type="image/jpeg"
        )


# ── Test Speech Service ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_speech_to_text_fallback():
    """Test speech_to_text returns client unavailable message when client fails."""
    res = await speech_to_text(b"audio_data")
    assert "text" in res
    assert "error" in res
    assert "not enabled" in res["error"].lower()


@pytest.mark.asyncio
async def test_text_to_speech_returns_none():
    """Test text_to_speech returns None when API credentials are not set."""
    res = await text_to_speech("Hello text")
    assert res is None


# ── Test Medication Service ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_check_drug_interactions_logic():
    """Test medication interaction check business logic."""
    # Test child age warning for Aspirin
    res = await check_drug_interactions(
        medications=["Aspirin"],
        patient_age=8,
    )
    assert res["safe_to_prescribe"] is False
    assert len(res["warnings"]) >= 1
    assert "Reye's syndrome" in res["warnings"][0]

    # Test allergy warning
    res = await check_drug_interactions(
        medications=["Penicillin"],
        patient_allergies=["penicillin"],
    )
    assert res["safe_to_prescribe"] is False
    assert len(res["allergy_warnings"]) >= 1

    # Test generic alternatives
    res = await check_drug_interactions(
        medications=["paracetamol"],
    )
    assert len(res["alternatives"]) >= 1
    assert res["alternatives"][0]["generic"] == "Acetaminophen"
