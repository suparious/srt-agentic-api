import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.agent import AgentConfig, MemoryConfig, LLMProviderConfig

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_create_agent(async_client: AsyncClient, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": {
            "llm_providers": [
                {
                    "provider_type": "mock",
                    "model_name": "mock-model"
                }
            ],
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
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    assert "agent_id" in response.json()

async def test_get_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["agent_id"] == test_agent
    assert agent["name"] == "Test Agent"
    assert "llm_providers" in agent["config"]
    assert isinstance(agent["config"]["llm_providers"], list)

async def test_update_agent(async_client: AsyncClient, auth_headers, test_agent):
    update_data = {
        "agent_config": {
            "temperature": 0.8,
            "llm_providers": [
                {
                    "provider_type": "openai",
                    "model_name": "gpt-4",
                    "api_key": "new-test-key"
                }
            ]
        }
    }
    response = await async_client.patch(f"/agent/{test_agent}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["message"] == "Agent updated successfully"

    # Verify the update
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    agent = response.json()
    assert agent["config"]["temperature"] == 0.8
    assert agent["config"]["llm_providers"][0]["model_name"] == "gpt-4"

async def test_delete_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.delete(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 204

    # Verify the agent is deleted
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 404

async def test_list_agents(async_client: AsyncClient, auth_headers, test_agent):
    # Create a second agent to ensure we have at least two
    await test_create_agent(async_client, auth_headers)

    response = await async_client.get("/agent", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) >= 2  # We should have at least the two agents we created
    for agent in agents:
        assert "agent_id" in agent
        assert "name" in agent
        assert "config" in agent
        assert "llm_providers" in agent["config"]
