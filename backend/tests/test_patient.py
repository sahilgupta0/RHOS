import pytest

def test_list_patients(client, auth_header):
    """Test retrieving list of patients."""
    response = client.get("/patients", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "patients" in data
    assert "total" in data
    assert len(data["patients"]) >= 1
    assert data["patients"][0]["name"] == "Dinesh Sharma"


def test_get_patient_details(client, auth_header):
    """Test retrieving details of a specific patient."""
    response = client.get("/patient/p001", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "p001"
    assert data["name"] == "Dinesh Sharma"


def test_get_patient_not_found(client, auth_header):
    """Test error when retrieving non-existent patient."""
    response = client.get("/patient/nonexistent", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found."


def test_create_patient(client, auth_header, mock_db_setup):
    """Test creating a new patient record."""
    payload = {
        "name": "Ramesh Gupta",
        "age": 52,
        "gender": "male",
        "phone": "+91-9988776655",
        "blood_group": "A+",
        "village_id": "v002",
        "asha_worker_id": "asha-002",
        "vitals": {
            "bp_sys": 120,
            "bp_dia": 80,
            "pulse": 72,
            "temperature": 98.6
        }
    }
    response = client.post("/patient", json=payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Ramesh Gupta"
    assert data["age"] == 52

    # Check if patient is stored in mock db
    assert data["id"] in mock_db_setup["patients"]
