def test_user_registration_success(client):
    payload = {
        "email": "new_engineer@enterprise.io",
        "password": "Password12345!",
        "full_name": "Dev Ops Lead",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["user"]["email"] == "new_engineer@enterprise.io"
    assert "token" in res["data"]
    assert "access_token" in res["data"]["token"]


def test_user_registration_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "DifferentPassword123!",
        "full_name": "Duplicate User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["success"] is False


def test_user_registration_invalid_password(client):
    payload = {
        "email": "short_pass@enterprise.io",
        "password": "short",
        "full_name": "Short Pass",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_user_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert "access_token" in res["data"]["token"]


def test_user_login_invalid_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "WrongPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["code"] == "AUTHENTICATION_FAILED"


def test_get_current_user_profile(client, test_user):
    # Login first
    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "Password123!"},
    ).json()
    token = login_res["data"]["token"]["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["id"] == test_user.id
    assert res["data"]["email"] == test_user.email


def test_auth_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

