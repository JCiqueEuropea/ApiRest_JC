import pytest
from fastapi.testclient import TestClient

from app.database.memory import fake_db, token_store
from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_db():
    fake_db.clear()
    token_store.clear()
    yield


@pytest.fixture
def sample_user_payload():
    return {
        "name": "Test User",
        "age": 25,
        "music_preferences": ["Rock", "Pop"]
    }


@pytest.fixture
def created_user(client, sample_user_payload):
    response = client.post("/users/", json=sample_user_payload)
    assert response.status_code == 201
    return response.json()
