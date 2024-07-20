import pytest
from fastapi.testclient import TestClient

def test_create_agent(test_client: TestClient, auth_headers):
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent",
        "model_name": "gpt-3.5-turbo"
    }
    response = test_client.post("/agent/", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    created_agent = response.json()
    assert created_agent["name"] == agent_data["name"]
    return created_agent["id"]

def test_get_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.get(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["id"] == agent_id

def test_update_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    update_data = {"description": "Updated test agent"}
    response = test_client.patch(f"/agent/{agent_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["description"] == update_data["description"]

def test_delete_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.delete(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 204

def test_list_agents(test_client: TestClient, auth_headers):
    response = test_client.get("/agent/", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
