import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings
from app.api.models import memory
from app.api.models.memory import MemoryType, MemoryOperation

test_settings = Settings()
client = TestClient(app)

@pytest.fixture
def agent_id():
    return str(uuid4())

def test_add_memory(agent_id):
    memory_data = {
        "agent_id": agent_id,
        "operation": MemoryOperation.ADD,
        "data": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = client.post(f"{test_settings.API_V1_STR}/memory/operate", json=memory_data)
    assert response.status_code == 200
    result = response.json()
    assert "memory_id" in result
    return result["memory_id"]

def test_retrieve_memory(agent_id):
    # First, add a memory
    memory_id = test_add_memory(agent_id)
    
    retrieve_data = {
        "agent_id": agent_id,
        "operation": MemoryOperation.RETRIEVE,
        "data": {"memory_id": memory_id}
    }
    response = client.post(f"{test_settings.API_V1_STR}/memory/operate", json=retrieve_data)
    assert response.status_code == 200
    result = response.json()
    assert "content" in result
    assert result["content"] == "Test memory content"

def test_search_memory(agent_id):
    # First, add a memory
    test_add_memory(agent_id)
    
    search_data = {
        "agent_id": agent_id,
        "operation": MemoryOperation.SEARCH,
        "query": "test query"
    }
    response = client.post(f"{test_settings.API_V1_STR}/memory/operate", json=search_data)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0
    assert "content" in results[0]

def test_memory_router_export():
    assert hasattr(memory, 'router'), "memory module should export 'router'"
    from app.api.endpoints.memory import router as internal_router
    assert memory.router == internal_router, "Exported router should be the same as the internal router"

def test_invalid_memory_operation(agent_id):
    invalid_data = {
        "agent_id": agent_id,
        "operation": "INVALID_OPERATION",
        "data": {"content": "This should fail"}
    }
    response = client.post(f"{test_settings.API_V1_STR}/memory/operate", json=invalid_data)
    assert response.status_code == 422  # Unprocessable Entity

def test_missing_agent_id():
    memory_data = {
        "operation": MemoryOperation.ADD,
        "data": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = client.post(f"{test_settings.API_V1_STR}/memory/operate", json=memory_data)
    assert response.status_code == 422  # Unprocessable Entity
