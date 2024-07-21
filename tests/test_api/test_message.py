import pytest
from fastapi.testclient import TestClient
from uuid import UUID
from app.core.agent import create_agent
from httpx import AsyncClient
from app.api.models.agent import AgentConfig, MemoryConfig

@pytest.fixture
async def test_agent(test_client: TestClient, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": AgentConfig(
            llm_provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ),
        "initial_prompt": "You are a helpful assistant."
    }
    agent_id = await create_agent(**agent_data)
    return agent_id

@pytest.mark.asyncio
async def test_send_message(test_client: AsyncClient, auth_headers, test_agent):
    agent_id = await test_agent
    message_data = {
        "agent_id": str(agent_id),
        "message": "Hello, agent!"
    }
    response = await test_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "agent_id" in result
    assert "response" in result
    assert isinstance(result.get("function_calls"), list) or result.get("function_calls") is None
    return result

@pytest.mark.asyncio
async def test_get_message_history(test_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(test_client, auth_headers, test_agent)

    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = await test_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    assert history["messages"][0]["content"] == "Hello, agent!"


def test_clear_message_history(test_client: TestClient, auth_headers):
    # First, send a message to ensure there's some history
    sent_message = test_send_message(test_client, auth_headers)

    clear_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = test_client.post("/message/clear", json=clear_request, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Message history cleared successfully"

    # Verify that the history is indeed cleared
    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = test_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history["messages"]) == 0


def test_get_latest_message(test_client: TestClient, auth_headers):
    # First, send a message
    sent_message = test_send_message(test_client, auth_headers)

    latest_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = test_client.get("/message/latest", params=latest_request, headers=auth_headers)
    assert response.status_code == 200
    latest_message = response.json()
    assert latest_message["content"] == "Hello, agent!"
