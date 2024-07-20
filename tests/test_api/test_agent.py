import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

def test_create_agent(test_client):
    # Test creating an agent
    pass

def test_get_agent(test_client):
    # Test retrieving an agent
    pass

def test_update_agent(test_client):
    # Test updating an agent
    pass

def test_delete_agent(test_client):
    # Test deleting an agent
    pass