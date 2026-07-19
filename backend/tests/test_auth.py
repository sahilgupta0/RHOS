# No setup imports needed
def test_login_success(client):
    """Test login with valid demo user credentials."""
    payload = {"email": "doctor@rhos.in", "password": "doctor123"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "doctor@rhos.in"
    assert data["user"]["role"] == "doctor"
    assert data["user"]["name"] == "Dr. Priya Sharma"


def test_login_invalid_credentials(client):
    """Test login fails with invalid credentials."""
    payload = {"email": "doctor@rhos.in", "password": "wrong-password"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "detail" in response.json()


def test_register_success(client, mock_db_setup):
    """Test registration of a new user."""
    payload = {
        "email": "new_nurse@rhos.in",
        "password": "secure_password",
        "name": "Nurse Joy",
        "role": "nurse",
        "phone": "+91-9999999999",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "new_nurse@rhos.in"
    assert data["user"]["role"] == "nurse"
    assert data["user"]["name"] == "Nurse Joy"


def test_register_duplicate_email(client):
    """Test registration fails with duplicate email."""
    payload = {
        "email": "doctor@rhos.in",
        "password": "another-password",
        "name": "Another Doctor",
        "role": "doctor",
        "phone": "+91-8888888888",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "detail" in response.json()


def test_me_endpoint_authenticated(client, auth_header):
    """Test get current user profile with valid credentials."""
    response = client.get("/auth/me", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "doctor@rhos.in"
    assert data["role"] == "doctor"


def test_me_endpoint_unauthorized(client):
    """Test get current user profile without authentication."""
    response = client.get("/auth/me")
    assert response.status_code == 401
