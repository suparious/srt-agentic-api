import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_send_message(async_client: AsyncClient, auth_headers, test_agent):
    message_data = {
        "agent_id": test_agent,
        "message": "Hello, agent!"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "agent_id" in result
    assert "response" in result
    assert isinstance(result.get("function_calls"), list) or result.get("function_calls") is None
    return result

async def test_get_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = await async_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    assert history["messages"][0]["content"] == "Hello, agent!"

async def test_clear_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    clear_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = await async_client.post("/message/clear", json=clear_request, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Message history cleared successfully"

    # Verify that the history is indeed cleared
    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = await async_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history["messages"]) == 0

async def test_get_latest_message(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    latest_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = await async_client.get("/message/latest", params=latest_request, headers=auth_headers)
    assert response.status_code == 200
    latest_message = response.json()
    assert latest_message["content"] == "Hello, agent!"
