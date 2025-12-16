from fastapi.testclient import TestClient
from app.main import app
import uuid


def test_register_login_create_calculation():
    # Use a unique username/email to avoid collisions
    unique = uuid.uuid4().hex[:8]
    username = f"user_{unique}"
    email = f"{unique}@example.com"
    password = "Passw0rd!"

    register_payload = {
        "first_name": "Flow",
        "last_name": "Test",
        "email": email,
        "username": username,
        "password": password,
        "confirm_password": password,
    }

    with TestClient(app) as client:
        # Register
        resp = client.post('/auth/register', json=register_payload)
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body.get('username') == username

        # Login
        login_payload = {"username": username, "password": password}
        resp = client.post('/auth/login', json=login_payload)
        assert resp.status_code == 200, resp.text
        token = resp.json().get('access_token')
        assert token

        headers = {"Authorization": f"Bearer {token}"}

        # Create calculation
        calc_payload = {"type": "addition", "inputs": [10.5, 3, 2]}
        resp = client.post('/calculations', json=calc_payload, headers=headers)
        assert resp.status_code == 201, resp.text
        calc = resp.json()
        assert calc['result'] == 15.5

        # List calculations and confirm created
        resp = client.get('/calculations', headers=headers)
        assert resp.status_code == 200, resp.text
        calcs = resp.json()
        assert any(c['id'] == calc['id'] for c in calcs)
