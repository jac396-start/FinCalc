from fastapi.testclient import TestClient
from app.main import app
from app.schemas.user import UserResponse
from uuid import uuid4
from datetime import datetime


def test_create_calc_with_nonexistent_user_token(monkeypatch):
    fake_user = UserResponse(
        id=uuid4(),
        username="unknown",
        email="unknown@example.com",
        first_name="Unknown",
        last_name="User",
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Override the dependency used by the route to bypass token auth
    from app.main import get_current_active_user
    app.dependency_overrides[get_current_active_user] = lambda: fake_user

    with TestClient(app) as client:
        resp = client.post('/calculations', json={"type": "addition", "inputs": [1, 2]})
        assert resp.status_code == 401
        assert 'Authenticated user not found' in resp.json().get('detail', '')

    # Clean up the dependency override
    app.dependency_overrides.pop(get_current_active_user, None)
