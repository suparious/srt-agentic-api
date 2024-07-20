# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    return {"X-API-Key": settings.API_KEY}
