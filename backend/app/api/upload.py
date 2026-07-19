"""
RHOS File Upload Endpoint.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.dependencies import CurrentUser
from app.schemas import UploadResponse
from app.services.firebase_storage import upload_file

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...), current_user: CurrentUser = None):
    """Upload a file to Firebase Storage."""
    try:
        contents = await file.read()
        result = await upload_file(
            file_data=contents,
            filename=file.filename or "upload",
            content_type=file.content_type or "application/octet-stream",
        )
        return UploadResponse(
            file_url=result["file_url"],
            file_name=result["file_name"],
            content_type=result["content_type"],
            size_bytes=len(contents),
        )
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Storage service unavailable.")
    except Exception as e:
        logger.error("Upload error: %s", e)
        raise HTTPException(status_code=500, detail="File upload failed.")
