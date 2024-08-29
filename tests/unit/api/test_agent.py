import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from app.core.models import AgentConfig, MemoryConfig, AgentCreationRequest
from app.core.agent_manager import AgentManager
from app.core.memory import MemorySystem
from app.core.llm_provider import LLMProvider
from app.core.function_manager import FunctionManager

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_agent_manager():
    return AsyncMock(spec=AgentManager)

@pytest.fixture
def mock_memory_system():
    return AsyncMock(spec=MemorySystem)

@pytest.fixture
def mock_llm_provider():
    return AsyncMock(spec=LLMProvider)

@pytest.fixture
def mock_function_manager(mock_factory):
    return mock_factory.create_mock(FunctionManager)

async def test_create_agent(async_client: AsyncClient, auth_headers, mock_agent_manager):
    agent_data = AgentCreationRequest(
        agent_name="Test Agent",
        agent_config=AgentConfig(
            llm_providers=[
                {
                    "provider_type": "mock",
                    "model_name": "mock-model"
                }
            ],
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ),
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ),
        initial_prompt="You are a helpful assistant."
    )

    mock_agent_manager.create_agent.return_value = UUID('12345678-1234-5678-1234-567812345678')

    response = await async_client.post("/agent/create", json=agent_data.dict(), headers=auth_headers)
    assert response.status_code == 201
    assert "agent_id" in response.json()
    assert response.json()["message"] == "Agent created successfully"

    mock_agent_manager.create_agent.assert_called_once_with(agent_data)

async def test_create_agent_validation_error(async_client: AsyncClient, auth_headers, mock_agent_manager):
    invalid_agent_data = {
        "agent_name": "Test Agent",
        "agent_config": {},  # Invalid config
        "memory_config": {},
        "initial_prompt": "You are a helpful assistant."
    }

    response = await async_client.post("/agent/create", json=invalid_agent_data, headers=auth_headers)
    assert response.status_code == 422  # Unprocessable Entity

async def test_create_agent_internal_error(async_client: AsyncClient, auth_headers, mock_agent_manager):
    agent_data = AgentCreationRequest(
        agent_name="Test Agent",
        agent_config=AgentConfig(
            llm_providers=[
                {
                    "provider_type": "mock",
                    "model_name": "mock-model"
                }
            ],
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ),
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ),
        initial_prompt="You are a helpful assistant."
    )

    mock_agent_manager.create_agent.side_effect = Exception("Internal error")

    response = await async_client.post("/agent/create", json=agent_data.dict(), headers=auth_headers)
    assert response.status_code == 500
    assert "Failed to create agent" in response.json()["detail"]

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
