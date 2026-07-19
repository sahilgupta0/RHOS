import pytest

def test_start_consultation(client, auth_header, mock_db_setup):
    """Test starting a new consultation session."""
    payload = {
        "patient_id": "p001",
        "chief_complaint": "Persistent headache",
        "language": "en"
    }
    response = client.post("/consultation/start", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["patient_id"] == "p001"
    assert data["chief_complaint"] == "Persistent headache"
    assert data["status"] == "active"

    # Verify created in db store
    assert data["id"] in mock_db_setup["consultations"]


def test_clear_consultation(client, auth_header, mock_db_setup):
    """Test clearing a consultation's history."""
    response = client.post("/consultation/c001/clear", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["conversation_history"] == []
    assert data["status"] == "active"


def test_clear_consultation_not_found(client, auth_header):
    """Test error when clearing non-existent consultation."""
    response = client.post("/consultation/nonexistent/clear", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Consultation not found."


def test_medication_check(client, auth_header, mock_db_setup):
    """Test medication interaction check endpoint."""
    payload = {
        "medications": ["Aspirin", "Ibuprofen"],
        "allergies": ["Penicillin"],
        "conditions": ["Hypertension"]
    }
    response = client.post("/consultation/medication/check", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "safety" in data
    assert "interactions" in data
    assert "recommendations" in data
