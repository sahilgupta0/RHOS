# No setup imports needed
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
        "gender": "Male",
        "phone": "+91-9988776655",
        "blood_group": "A+",
        "village_id": "v002",
        "asha_worker_id": "asha-002",
        "vitals": {"bp_sys": 120, "bp_dia": 80, "pulse": 72, "temperature": 98.6},
    }
    response = client.post("/patient", json=payload, headers=auth_header)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Ramesh Gupta"
    assert data["age"] == 52

    # Check if patient is stored in mock db
    assert data["id"] in mock_db_setup["patients"]


def test_update_patient_success(client, auth_header, mock_db_setup):
    """Test updating an existing patient record."""
    payload = {"phone": "+91-9999999999", "address": "New Outpost Address"}
    response = client.put("/patient/p001", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+91-9999999999"
    assert data["address"] == "New Outpost Address"
    assert mock_db_setup["patients"]["p001"]["phone"] == "+91-9999999999"
    assert mock_db_setup["patients"]["p001"]["address"] == "New Outpost Address"


def test_update_patient_not_found(client, auth_header):
    """Test updating a non-existent patient record returns 404."""
    payload = {"phone": "+91-9999999999"}
    response = client.put("/patient/nonexistent", json=payload, headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found."


def test_get_patient_history_success(client, auth_header):
    """Test retrieving complete medical history for a patient."""
    response = client.get("/patient/history/p001", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "patient" in data
    assert "medical_history" in data
    assert "vitals" in data
    assert "allergies" in data
    assert data["patient"]["id"] == "p001"


def test_get_patient_history_not_found(client, auth_header):
    """Test retrieving history for non-existent patient returns 404."""
    response = client.get("/patient/history/nonexistent", headers=auth_header)
    assert response.status_code == 404


def test_list_patients_search(client, auth_header):
    """Test listing patients with search query."""
    response = client.get("/patients?search=Dinesh", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data["patients"]) >= 1


def test_list_patients_village_filter(client, auth_header):
    """Test listing patients filtered by village ID."""
    response = client.get("/patients?village_id=v001", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "patients" in data

