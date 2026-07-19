"""
RHOS FastAPI Dependencies.

Dependency injection providers for routes.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings
from app.core.firebase_init import get_firestore_client, is_firebase_initialized
from app.core.security import decode_access_token
from app.schemas import UserResponse

logger = logging.getLogger(__name__)


# ── Settings ───────────────────────────────────────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]


# ── Authentication ─────────────────────────────────────────────────────────────


async def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserResponse:
    """
    Authenticate the current user from the Authorization header.

    Supports both Firebase Auth tokens and local JWT tokens based on AUTH_MODE.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ", 1)[1]

    if settings.auth_mode == "firebase" and is_firebase_initialized():
        return await _verify_firebase_token(token)
    else:
        return _verify_local_token(token)


async def _verify_firebase_token(token: str) -> UserResponse:
    """Verify a Firebase ID token."""
    try:
        from firebase_admin import auth as firebase_auth

        decoded = firebase_auth.verify_id_token(token)
        return UserResponse(
            id=decoded.get("uid", ""),
            email=decoded.get("email", ""),
            name=decoded.get("name", decoded.get("email", "User")),
            role="doctor",
            avatar_url=decoded.get("picture", ""),
        )
    except Exception as e:
        logger.error("Firebase token verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


def _verify_local_token(token: str) -> UserResponse:
    """Verify a local JWT token."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    return UserResponse(
        id=payload.get("sub", ""),
        email=payload.get("email", ""),
        name=payload.get("name", "User"),
        role=payload.get("role", "doctor"),
        patient_id=payload.get("patient_id", ""),
    )


# ── Optional Auth (for public endpoints that benefit from auth) ────────────────


async def get_optional_user(
    authorization: str | None = Header(None, alias="Authorization"),
    settings: Settings = Depends(get_settings),
) -> UserResponse | None:
    """Get current user if authenticated, None otherwise."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization, settings)
    except HTTPException:
        return None


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
OptionalUser = Annotated[UserResponse | None, Depends(get_optional_user)]
