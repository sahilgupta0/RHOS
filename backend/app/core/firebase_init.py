"""
RHOS Firebase Initialization.

Singleton initialization of Firebase Admin SDK for Firestore and Storage.
"""

from __future__ import annotations

import logging
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore, storage

from app.config import get_settings

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None
_firestore_client = None
_storage_bucket = None


def init_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call multiple times."""
    global _firebase_app

    if _firebase_app is not None:
        return

    settings = get_settings()
    cred_path = Path(settings.firebase_credentials)

    if not cred_path.exists():
        logger.warning(
            "Firebase credentials file not found at '%s'. "
            "Firebase features will be unavailable. "
            "Set FIREBASE_CREDENTIALS in .env to enable.",
            cred_path,
        )
        return

    try:
        cred = credentials.Certificate(str(cred_path))
        _firebase_app = firebase_admin.initialize_app(
            cred,
            {"storageBucket": settings.firebase_storage_bucket} if settings.firebase_storage_bucket else {},
        )
        logger.info("Firebase Admin SDK initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize Firebase: %s", e)


def get_firestore_client():
    """Get the Firestore client instance."""
    global _firestore_client
    if _firestore_client is None:
        if _firebase_app is None:
            logger.warning("Firebase not initialized. Returning None for Firestore client.")
            return None
        _firestore_client = firestore.client()
    return _firestore_client


def get_storage_bucket():
    """Get the Firebase Storage bucket instance."""
    global _storage_bucket
    if _storage_bucket is None:
        if _firebase_app is None:
            logger.warning("Firebase not initialized. Returning None for Storage bucket.")
            return None
        _storage_bucket = storage.bucket()
    return _storage_bucket


def is_firebase_initialized() -> bool:
    """Check if Firebase has been successfully initialized."""
    return _firebase_app is not None
