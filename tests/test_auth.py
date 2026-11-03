import json

def test_register_success(client):
    """Test successful user registration."""
    payload = {
        "email": "newuser@company.com",
        "password": "StrongPassword123!",
        "full_name": "New User",
        "role": "analyst"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "newuser@company.com"
    assert data["user"]["role"] == "analyst"


def test_register_duplicate_email(client, admin_user):
    """Test registration with existing email returns 409 Conflict."""
    payload = {
        "email": admin_user.email,
        "password": "Password123!",
        "full_name": "Duplicate User"
    }
    res = client.post("/api/v1/auth/register", json=payload)
    assert res.status_code == 409
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT_ERROR"


def test_login_success(client, admin_user):
    """Test login with valid credentials."""
    payload = {
        "email": admin_user.email,
        "password": "AdminPass123!"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["role"] == "admin"


def test_login_invalid_password(client, admin_user):
    """Test login with incorrect password returns 401."""
    payload = {
        "email": admin_user.email,
        "password": "WrongPassword!"
    }
    res = client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False


def test_get_current_user(client, admin_headers):
    """Test accessing /me with JWT token."""
    res = client.get("/api/v1/auth/me", headers=admin_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["user"]["email"] == "test_admin@company.com"


def test_get_current_user_unauthorized(client):
    """Test accessing /me without token returns 401."""
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
