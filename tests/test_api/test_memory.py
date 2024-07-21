import pytest
from fastapi.testclient import TestClient
from uuid import UUID

def test_add_memory(test_client: TestClient, auth_headers):
    memory_data = {
        "agent_id": str(UUID(int=0)),  # Using a dummy UUID for testing
        "memory_type": "SHORT_TERM",
        "entry": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = test_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert added_memory["message"] == "Memory added successfully"
    assert "memory_id" in added_memory
    return added_memory["memory_id"]

def test_retrieve_memory(test_client: TestClient, auth_headers):
    memory_id = test_add_memory(test_client, auth_headers)
    retrieve_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "memory_id": memory_id
    }
    response = test_client.get("/memory/retrieve", params=retrieve_data, headers=auth_headers)
    assert response.status_code == 200
    memory = response.json()
    assert memory["content"] == "Test memory content"
    assert memory["metadata"] == {"key": "value"}

def test_search_memory(test_client: TestClient, auth_headers):
    test_add_memory(test_client, auth_headers)  # Add a memory to search for
    search_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "query": "Test memory",
        "limit": 5
    }
    response = test_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0

def test_delete_memory(test_client: TestClient, auth_headers):
    memory_id = test_add_memory(test_client, auth_headers)
    delete_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "memory_id": memory_id
    }
    response = test_client.delete("/memory/delete", params=delete_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Memory deleted successfully"

def test_memory_operation(test_client: TestClient, auth_headers):
    operation_data = {
        "agent_id": str(UUID(int=0)),
        "operation": "ADD",
        "memory_type": "SHORT_TERM",
        "data": {
            "content": "Test operation memory content",
            "metadata": {"operation": "test"}
        }
    }
    response = test_client.post("/memory/operate", json=operation_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "ADD operation completed successfully"
    assert "result" in result