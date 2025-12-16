from uuid import uuid4

from fastapi.testclient import TestClient


def test_calculation_path_param_present_in_openapi():
    """OpenAPI should document the `calc_id` path parameter with an example for GET/PUT/DELETE."""
    from app.main import app

    with TestClient(app) as client:
        spec = client.get("/openapi.json").json()

    for method in ("get", "put", "delete"):
        path_item = spec["paths"]["/calculations/{calc_id}"][method]

        # Parameter exists and is a path param with an example
        params = [p for p in path_item.get("parameters", []) if p.get("name") == "calc_id"]
        assert params, f"missing calc_id parameter in {method} operation"
        p = params[0]
        assert p["in"] == "path"
        assert p["required"] is True
        assert p.get("description", "").startswith("UUID of the calculation")
        assert p.get("example") == "123e4567-e89b-12d3-a456-426614174999"

        # 404 responses should include guidance about listing IDs
        resp_404 = path_item["responses"].get("404")
        assert resp_404 is not None
        assert "Ensure the ID exists" in resp_404.get("description", "")


def test_get_nonexistent_calculation_returns_informative_404():
    """GETting a calc ID that doesn't exist (but is well-formed) returns the expected 404 JSON detail."""
    from app.main import app

    payload = {
        "confirm_password": "SecurePass123!",
        "email": "ui.user@example.com",
        "first_name": "UI",
        "last_name": "User",
        "password": "SecurePass123!",
        "username": f"uiuser_{uuid4().hex[:6]}",
    }

    with TestClient(app) as client:
        # register + login
        r = client.post("/auth/register", json=payload)
        assert r.status_code == 201
        login = {"username": payload["username"], "password": payload["password"]}
        r = client.post("/auth/login", json=login)
        assert r.status_code == 200
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        fake_id = str(uuid4())
        r = client.get(f"/calculations/{fake_id}", headers=headers)
        assert r.status_code == 404
        assert r.json()["detail"].startswith("Calculation not found")
