import pytest
from fastapi.testclient import TestClient

def test_store_memory(test_client: TestClient, auth_headers):
    memory_data = {
        "agent_id": "test_agent_id",
        "key": "test_key",
        "value": "Test memory value"
    }
    response = test_client.post("/memory/", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    stored_memory = response.json()
    assert stored_memory["key"] == memory_data["key"]
    return stored_memory["id"]

def test_retrieve_memory(test_client: TestClient, auth_headers):
    memory_id = test_store_memory(test_client, auth_headers)
    response = test_client.get(f"/memory/{memory_id}", headers=auth_headers)
    assert response.status_code == 200
    memory = response.json()
    assert memory["id"] == memory_id

def test_update_memory(test_client: TestClient, auth_headers):
    memory_id = test_store_memory(test_client, auth_headers)
    update_data = {"value": "Updated memory value"}
    response = test_client.patch(f"/memory/{memory_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_memory = response.json()
    assert updated_memory["value"] == update_data["value"]

def test_delete_memory(test_client: TestClient, auth_headers):
    memory_id = test_store_memory(test_client, auth_headers)
    response = test_client.delete(f"/memory/{memory_id}", headers=auth_headers)
    assert response.status_code == 204

def test_list_memories(test_client: TestClient, auth_headers):
    response = test_client.get("/memory/", headers=auth_headers)
    assert response.status_code == 200
    memories = response.json()
    assert isinstance(memories, list)
