"""
RHOS Firestore Service.

Provides async Firestore client access and helpers.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.firebase_init import get_firestore_client

logger = logging.getLogger(__name__)


async def get_document(collection: str, doc_id: str) -> dict[str, Any] | None:
    """Retrieve a document from a collection by ID."""
    db = get_firestore_client()
    if db is None:
        logger.warning("Firestore client not initialized. Cannot get document.")
        return None
    try:
        doc_ref = db.collection(collection).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        return None
    except Exception as e:
        logger.error("Error retrieving document %s/%s: %s", collection, doc_id, e)
        return None


async def save_document(
    collection: str, data: dict[str, Any], doc_id: str | None = None
) -> str:
    """Save a document to a collection. Returns document ID."""
    db = get_firestore_client()
    if db is None:
        raise ConnectionError("Firestore client not initialized.")
    try:
        if doc_id:
            db.collection(collection).document(doc_id).set(data)
            return doc_id
        else:
            _, doc_ref = db.collection(collection).add(data)
            return doc_ref.id
    except Exception as e:
        logger.error("Error saving document to %s: %s", collection, e)
        raise
