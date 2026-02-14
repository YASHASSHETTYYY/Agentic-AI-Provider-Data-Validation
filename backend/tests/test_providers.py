from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def _auth_header(client: TestClient) -> dict[str, str]:
    email = f"provider-user-{uuid4().hex}@example.com"
    password = "ProviderPass123!"

    register = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_provider_import_and_summary() -> None:
    csv_payload = (
        "provider_name,specialty,npi,phone,address\n"
        "Dr. Jane Smith,Cardiology,1234567890,5551234567,123 Main Street\n"
        "Dr. John Doe,Pediatrics,12345,55512345,1 A St\n"
    )

    with TestClient(app) as client:
        headers = _auth_header(client)
        files = {"file": ("providers.csv", csv_payload, "text/csv")}

        imported = client.post("/api/v1/providers/import-csv", files=files, headers=headers)
        assert imported.status_code == 201
        assert imported.json()["imported"] == 2

        listed = client.get("/api/v1/providers", headers=headers)
        assert listed.status_code == 200
        list_payload = listed.json()
        assert list_payload["total"] >= 2
        assert len(list_payload["items"]) >= 2

        summary = client.get("/api/v1/providers/summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["total_providers"] >= 2
