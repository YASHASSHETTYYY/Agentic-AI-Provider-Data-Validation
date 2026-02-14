from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_and_login() -> None:
    email = f"user-{uuid4().hex}@example.com"
    password = "IndustrialPass123!"

    with TestClient(app) as client:
        register = client.post(
            "/api/v1/auth/register",
            json={"email": email, "password": password},
        )
        assert register.status_code == 201

        login = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login.status_code == 200
        payload = login.json()
        assert "access_token" in payload
        assert payload["token_type"] == "bearer"
