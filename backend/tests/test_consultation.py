# No setup imports needed
def test_start_consultation(client, auth_header, mock_db_setup):
    """Test starting a new consultation session."""
    payload = {
        "patient_id": "p001",
        "chief_complaint": "Persistent headache",
        "language": "en",
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
        "conditions": ["Hypertension"],
    }
    response = client.post("/medicine/check", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "safe_to_prescribe" in data
    assert "interactions" in data
    assert "warnings" in data
    assert "alternatives" in data


def test_get_consultation_details(client, auth_header):
    """Test retrieving details of an active consultation."""
    response = client.get("/consultation/c001", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "c001"
    assert data["patient_id"] == "p001"
    assert data["status"] == "active"


def test_get_consultation_not_found(client, auth_header):
    """Test error when retrieving non-existent consultation."""
    response = client.get("/consultation/nonexistent", headers=auth_header)
    assert response.status_code == 404
    assert response.json()["detail"] == "Consultation not found."


def test_list_consultations(client, auth_header):
    """Test listing recent consultations."""
    response = client.get("/consultations", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_consultations_by_patient(client, auth_header):
    """Test listing consultations filtered by patient ID."""
    response = client.get("/consultations?patient_id=p001", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["patient_id"] == "p001"


def test_consultation_chat_success(client, auth_header, mock_db_setup):
    """Test sending a patient message in the chat phase."""
    payload = {"consultation_id": "c001", "message": "I have a cough"}
    response = client.post("/consultation/chat", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["consultation_id"] == "c001"
    assert "agent_response" in data
    # Verify message appended to db store
    assert len(mock_db_setup["consultations"]["c001"]["conversation_history"]) >= 1


def test_consultation_chat_not_found(client, auth_header):
    """Test chat route returns 404 if consultation not found."""
    payload = {"consultation_id": "nonexistent", "message": "Hello"}
    response = client.post("/consultation/chat", json=payload, headers=auth_header)
    assert response.status_code == 404


def test_consultation_submit_success(client, auth_header, mock_db_setup):
    """Test submitting consultation to run the full clinical pipeline."""
    payload = {"consultation_id": "c001"}
    response = client.post("/consultation/submit", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["consultation_id"] == "c001"
    assert data["triage_priority"] == "MEDIUM"
    assert mock_db_setup["consultations"]["c001"]["status"] == "submitted"


def test_consultation_submit_not_found(client, auth_header):
    """Test submit route returns 404 if consultation not found."""
    payload = {"consultation_id": "nonexistent"}
    response = client.post("/consultation/submit", json=payload, headers=auth_header)
    assert response.status_code == 404


def test_consultation_upload_image(client, auth_header):
    """Test uploading a consultation medical image for vision analysis."""
    files = {"file": ("xray.jpg", b"mock_xray_image_bytes", "image/jpeg")}
    data = {"consultation_id": "c001"}
    response = client.post("/consultation/upload", files=files, data=data, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert "findings" in data
    assert "disclaimer" in data


def test_run_triage_classification(client, auth_header):
    """Test independent triage classification route."""
    payload = {
        "patient_id": "p001",
        "symptoms": ["fever", "cough"],
        "vitals": {"temp": 101.2},
        "medical_history": ["asthma"],
        "age": 45,
        "gender": "Female",
    }
    response = client.post("/triage", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == "MEDIUM"
    assert "reasoning" in data


def test_generate_summary_route(client, auth_header):
    """Test clinical summary SOAP generation endpoint."""
    payload = {"consultation_id": "c001"}
    response = client.post("/summary", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["consultation_id"] == "c001"
    assert "summary" in data
    assert "assessment" in data

