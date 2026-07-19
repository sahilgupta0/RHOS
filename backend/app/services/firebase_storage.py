"""
RHOS Firebase Storage Service.

File upload/download and signed URL generation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import timedelta
from typing import BinaryIO

from app.core.firebase_init import get_storage_bucket

logger = logging.getLogger(__name__)


async def upload_file(
    file_data: bytes | BinaryIO,
    filename: str,
    content_type: str = "application/octet-stream",
    folder: str = "uploads",
) -> dict[str, str]:
    """
    Upload a file to Firebase Storage.

    Returns dict with file_url, file_name, and storage_path.
    """
    bucket = get_storage_bucket()
    if bucket is None:
        raise ConnectionError("Firebase Storage is not initialized.")

    try:
        # Generate unique filename
        unique_name = f"{uuid.uuid4().hex[:12]}_{filename}"
        storage_path = f"{folder}/{unique_name}"

        blob = bucket.blob(storage_path)
        blob.content_type = content_type

        if isinstance(file_data, bytes):
            blob.upload_from_string(file_data, content_type=content_type)
        else:
            blob.upload_from_file(file_data, content_type=content_type)

        # Make publicly accessible or generate signed URL
        blob.make_public()
        public_url = blob.public_url

        logger.info("File uploaded to %s", storage_path)

        return {
            "file_url": public_url,
            "file_name": unique_name,
            "storage_path": storage_path,
            "content_type": content_type,
        }
    except Exception as e:
        logger.error("Error uploading file: %s", e)
        raise


async def get_signed_url(storage_path: str, expiration_hours: int = 1) -> str:
    """Generate a signed URL for a file."""
    bucket = get_storage_bucket()
    if bucket is None:
        raise ConnectionError("Firebase Storage is not initialized.")

    blob = bucket.blob(storage_path)
    url = blob.generate_signed_url(
        expiration=timedelta(hours=expiration_hours),
        method="GET",
    )
    return url


async def delete_file(storage_path: str) -> None:
    """Delete a file from Firebase Storage."""
    bucket = get_storage_bucket()
    if bucket is None:
        raise ConnectionError("Firebase Storage is not initialized.")

    blob = bucket.blob(storage_path)
    blob.delete()
    logger.info("File deleted: %s", storage_path)
