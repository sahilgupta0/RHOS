"""
RHOS Firebase Initialization.

Singleton initialization of Firebase Admin SDK for Firestore and Storage.
Supports credentials from a local file path OR a JSON string in the
FIREBASE_CREDENTIALS_JSON environment variable (preferred for production).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore, storage

from app.config import get_settings

logger = logging.getLogger(__name__)

_firebase_app: firebase_admin.App | None = None
_firestore_client = None
_storage_bucket = None


def init_firebase() -> None:
    """Initialize Firebase Admin SDK. Safe to call multiple times.

    Credential resolution order:
    1. FIREBASE_CREDENTIALS_JSON env var (JSON string — preferred in production)
    2. File path from settings.firebase_credentials (local dev / Docker volume)
    """
    global _firebase_app

    if _firebase_app is not None:
        return

    settings = get_settings()

    # 1. Try JSON string from environment variable (production / CI)
    cred_json_str = os.environ.get("FIREBASE_CREDENTIALS_JSON", "").strip()
    if cred_json_str:
        try:
            cred_dict = json.loads(cred_json_str)
            cred = credentials.Certificate(cred_dict)
            _firebase_app = firebase_admin.initialize_app(
                cred,
                (
                    {"storageBucket": settings.firebase_storage_bucket}
                    if settings.firebase_storage_bucket
                    else {}
                ),
            )
            logger.info(
                "Firebase Admin SDK initialized from FIREBASE_CREDENTIALS_JSON env var."
            )
            return
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                "Invalid JSON in FIREBASE_CREDENTIALS_JSON: %s. Falling back to file.", e
            )

    # 2. Try local file path (local development / Docker volume mount)
    cred_path = Path(settings.firebase_credentials)
    if not cred_path.exists():
        logger.warning(
            "Firebase credentials file not found at '%s'. "
            "Firebase features will be unavailable. "
            "Set FIREBASE_CREDENTIALS_JSON or FIREBASE_CREDENTIALS in .env to enable.",
            cred_path,
        )
        return

    try:
        cred = credentials.Certificate(str(cred_path))
        _firebase_app = firebase_admin.initialize_app(
            cred,
            (
                {"storageBucket": settings.firebase_storage_bucket}
                if settings.firebase_storage_bucket
                else {}
            ),
        )
        logger.info("Firebase Admin SDK initialized from credentials file.")
    except Exception as e:
        logger.error("Failed to initialize Firebase: %s", e)


def get_firestore_client():
    """Get the Firestore client instance."""
    global _firestore_client
    if _firestore_client is None:
        if _firebase_app is None:
            logger.warning(
                "Firebase not initialized. Returning None for Firestore client."
            )
            return None
        _firestore_client = firestore.client()
    return _firestore_client


def get_storage_bucket():
    """Get the Firebase Storage bucket instance."""
    global _storage_bucket
    if _storage_bucket is None:
        if _firebase_app is None:
            logger.warning(
                "Firebase not initialized. Returning None for Storage bucket."
            )
            return None
        _storage_bucket = storage.bucket()
    return _storage_bucket


def is_firebase_initialized() -> bool:
    """Check if Firebase has been successfully initialized."""
    return _firebase_app is not None
