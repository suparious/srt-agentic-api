import pytest
from fastapi.testclient import TestClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_create_agent(test_client: TestClient, auth_headers):
    agent_data = {
        "name": "Test Agent",
        "config": {
            "llm_provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150,
            "memory_config": {
                "use_long_term_memory": True,
                "use_redis_cache": True
            }
        },
        "memory_config": {
            "use_long_term_memory": True,
            "use_redis_cache": True
        },
        "initial_prompt": "You are a helpful assistant."
    }
    response = await test_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    created_agent = response.json()
    assert created_agent["message"] == "Agent created successfully"
    assert UUID(created_agent["agent_id"])
    return created_agent["agent_id"]

async def test_get_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.get(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["agent_id"] == str(agent_id)
    assert agent["name"] == "Test Agent"

async def test_update_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    update_data = {
        "agent_config": {
            "temperature": 0.8
        }
    }
    response = test_client.patch(f"/agent/{agent_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["message"] == "Agent updated successfully"

async def test_delete_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.delete(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 204

async def test_list_agents(test_client: TestClient, auth_headers):
    # Create a couple of agents first
    test_create_agent(test_client, auth_headers)
    test_create_agent(test_client, auth_headers)

    response = test_client.get("/agent/", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) >= 2  # We should have at least the two agents we just created