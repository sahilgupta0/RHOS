from __future__ import annotations

from unittest.mock import AsyncMock, patch


@patch("app.api.upload.upload_file", new_callable=AsyncMock)
def test_upload_success(mock_upload, client, auth_header):
    """Test successful file upload endpoint."""
    mock_upload.return_value = {
        "file_url": "https://storage.googleapis.com/rhos/image.jpg",
        "file_name": "image.jpg",
        "content_type": "image/jpeg",
    }

    files = {"file": ("image.jpg", b"fake_image_bytes", "image/jpeg")}
    response = client.post("/upload", files=files, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["file_url"] == "https://storage.googleapis.com/rhos/image.jpg"
    assert data["file_name"] == "image.jpg"
    assert data["size_bytes"] == len(b"fake_image_bytes")
    mock_upload.assert_called_once_with(
        file_data=b"fake_image_bytes",
        filename="image.jpg",
        content_type="image/jpeg",
    )


@patch("app.api.upload.upload_file", new_callable=AsyncMock)
def test_upload_service_unavailable(mock_upload, client, auth_header):
    """Test file upload endpoint when connection error raised."""
    mock_upload.side_effect = ConnectionError("Firebase not initialized")

    files = {"file": ("image.jpg", b"fake_image_bytes", "image/jpeg")}
    response = client.post("/upload", files=files, headers=auth_header)
    assert response.status_code == 503
    assert response.json()["detail"] == "Storage service unavailable."


@patch("app.api.upload.upload_file", new_callable=AsyncMock)
def test_upload_general_failure(mock_upload, client, auth_header):
    """Test file upload endpoint on general exceptions."""
    mock_upload.side_effect = Exception("General error")

    files = {"file": ("image.jpg", b"fake_image_bytes", "image/jpeg")}
    response = client.post("/upload", files=files, headers=auth_header)
    assert response.status_code == 500
    assert response.json()["detail"] == "File upload failed."
