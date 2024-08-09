import pytest
from uuid import UUID
from datetime import datetime
from app.api.models.message import (
    MessageRequest,
    FunctionCall,
    MessageResponse,
    MessageHistoryRequest,
    MessageHistoryItem,
    MessageHistoryResponse
)

def test_message_request():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    message_request = MessageRequest(
        agent_id=agent_id,
        content="Hello, agent!",
        metadata={"key": "value"}
    )
    assert message_request.agent_id == agent_id
    assert message_request.content == "Hello, agent!"
    assert message_request.metadata == {"key": "value"}

def test_function_call():
    function_call = FunctionCall(
        name="test_function",
        arguments={"arg1": 1, "arg2": "test"}
    )
    assert function_call.name == "test_function"
    assert function_call.arguments == {"arg1": 1, "arg2": "test"}

def test_message_response():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    function_call = FunctionCall(name="test_function", arguments={"arg1": 1})
    message_response = MessageResponse(
        agent_id=agent_id,
        content="Response from agent",
        function_calls=[function_call],
        metadata={"response_key": "response_value"}
    )
    assert message_response.agent_id == agent_id
    assert message_response.content == "Response from agent"
    assert len(message_response.function_calls) == 1
    assert message_response.function_calls[0].name == "test_function"
    assert message_response.metadata == {"response_key": "response_value"}

def test_message_history_request():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    history_request = MessageHistoryRequest(
        agent_id=agent_id,
        limit=50,
        before="2023-01-01T00:00:00Z"
    )
    assert history_request.agent_id == agent_id
    assert history_request.limit == 50
    assert history_request.before == "2023-01-01T00:00:00Z"

def test_message_history_item():
    history_item = MessageHistoryItem(
        id="msg123",
        timestamp="2023-01-01T12:00:00Z",
        sender="user",
        content="Test message",
        metadata={"item_key": "item_value"}
    )
    assert history_item.id == "msg123"
    assert history_item.timestamp == "2023-01-01T12:00:00Z"
    assert history_item.sender == "user"
    assert history_item.content == "Test message"
    assert history_item.metadata == {"item_key": "item_value"}

def test_message_history_response():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    history_item = MessageHistoryItem(
        id="msg123",
        timestamp="2023-01-01T12:00:00Z",
        sender="user",
        content="Test message"
    )
    history_response = MessageHistoryResponse(
        agent_id=agent_id,
        messages=[history_item],
        has_more=False
    )
    assert history_response.agent_id == agent_id
    assert len(history_response.messages) == 1
    assert history_response.messages[0].id == "msg123"
    assert history_response.has_more == False

def test_message_request_validation():
    with pytest.raises(ValueError):
        MessageRequest(agent_id="invalid_uuid", content="Test")

def test_message_history_request_validation():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    with pytest.raises(ValueError):
        MessageHistoryRequest(agent_id=agent_id, limit=101)  # Exceeds max limit

    with pytest.raises(ValueError):
        MessageHistoryRequest(agent_id=agent_id, limit=0)  # Below min limit
