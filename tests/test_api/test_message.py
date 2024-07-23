import pytest
from httpx import AsyncClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

async def test_send_message(async_client: AsyncClient, auth_headers, test_agent):
    message_data = {
        "agent_id": test_agent,
        "content": "Hello, agent!"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "agent_id" in result
    assert result["agent_id"] == test_agent
    assert "content" in result
    assert isinstance(result["content"], str)
    assert isinstance(result.get("function_calls", []), list)
    return result

async def test_get_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.get(f"/message/history?agent_id={test_agent}&limit=10", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert "agent_id" in history
    assert history["agent_id"] == test_agent
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    assert history["messages"][0]["content"] == "Hello, agent!"

async def test_clear_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.post(f"/message/clear", json={"agent_id": test_agent}, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Message history cleared successfully"

    # Verify that the history is indeed cleared
    response = await async_client.get(f"/message/history?agent_id={test_agent}&limit=10", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history["messages"]) == 0

async def test_get_latest_message(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.get(f"/message/latest?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    latest_message = response.json()
    assert latest_message["content"] == "Hello, agent!"

async def test_send_message_invalid_agent(async_client: AsyncClient, auth_headers):
    invalid_agent_id = str(UUID(int=0))
    message_data = {
        "agent_id": invalid_agent_id,
        "content": "This should fail"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()
