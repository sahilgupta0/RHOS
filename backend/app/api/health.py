"""
RHOS Health Check Endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.core.firebase_init import is_firebase_initialized
from app.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        firebase_connected=is_firebase_initialized(),
        gemini_configured=settings.is_gemini_configured,
    )
