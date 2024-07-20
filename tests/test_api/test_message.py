import pytest
from fastapi.testclient import TestClient

def test_create_message(test_client: TestClient, auth_headers):
    message_data = {
        "agent_id": "test_agent_id",
        "content": "Hello, agent!",
        "role": "user"
    }
    response = test_client.post("/message/", json=message_data, headers=auth_headers)
    assert response.status_code == 201
    created_message = response.json()
    assert created_message["content"] == message_data["content"]
    return created_message["id"]

def test_get_message(test_client: TestClient, auth_headers):
    message_id = test_create_message(test_client, auth_headers)
    response = test_client.get(f"/message/{message_id}", headers=auth_headers)
    assert response.status_code == 200
    message = response.json()
    assert message["id"] == message_id

def test_list_messages(test_client: TestClient, auth_headers):
    response = test_client.get("/message/", headers=auth_headers)
    assert response.status_code == 200
    messages = response.json()
    assert isinstance(messages, list)
