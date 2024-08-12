import pytest
from httpx import AsyncClient
from uuid import UUID
from unittest.mock import patch
from app.core.function_manager import FunctionManager

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_function_manager():
    with patch('app.api.endpoints.function.function_manager') as mock:
        yield mock


async def test_register_function(async_client: AsyncClient, auth_headers, mock_function_manager):
    function_data = {
        "function": {
            "name": "test_function",
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                }
            },
            "return_type": "string"
        }
    }
    mock_function_manager.register_function.return_value = "mock_function_id"

    response = await async_client.post("/function/register", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    assert "function_id" in response.json()
    assert response.json()["message"] == "Function registered successfully"

    mock_function_manager.register_function.assert_called_once()
    return response.json()["function_id"]


async def test_get_function(async_client: AsyncClient, auth_headers, mock_function_manager):
    # First, register a function
    function_id = await test_register_function(async_client, auth_headers, mock_function_manager)

    # Mock the get_function method
    mock_function_manager.get_function.return_value = {
        "name": "test_function",
        "description": "A test function",
        "parameters": {},
        "return_type": "string"
    }

    response = await async_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "test_function"

async def test_update_function(async_client: AsyncClient, auth_headers, mock_function_manager):
    function_id = await test_register_function(async_client, auth_headers, mock_function_manager)
    update_data = {
        "function_id": function_id,
        "updated_function": {
            "name": "updated_test_function",
            "description": "An updated test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"},
                    "param3": {"type": "boolean"}
                }
            },
            "return_type": "string"
        }
    }
    response = await async_client.put("/function/update", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Function updated successfully"

async def test_delete_function(async_client: AsyncClient, auth_headers, test_agent):
    function_id = await test_register_function(async_client, auth_headers)
    response = await async_client.delete(f"/function/{function_id}?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Function removed successfully"

async def test_list_functions(async_client: AsyncClient, auth_headers, test_agent):
    # Register a couple of functions first
    await test_register_function(async_client, auth_headers)
    await test_register_function(async_client, auth_headers)

    response = await async_client.get(f"/function/available?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    functions = response.json()
    assert "functions" in functions
    assert isinstance(functions["functions"], list)
    assert len(functions["functions"]) >= 2  # We should have at least the two functions we just registered


async def test_execute_function(async_client: AsyncClient, auth_headers, mock_function_manager):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    execution_data = {
        "agent_id": str(agent_id),
        "function_name": "test_function",
        "parameters": {
            "param1": "test",
            "param2": 123
        }
    }
    mock_function_manager.execute_function.return_value = "Function executed successfully"

    response = await async_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert result["result"] == "Function executed successfully"

    mock_function_manager.execute_function.assert_called_once()

async def test_execute_nonexistent_function(async_client: AsyncClient, auth_headers, mock_function_manager):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    execution_data = {
        "agent_id": str(agent_id),
        "function_name": "nonexistent_function",
        "parameters": {}
    }
    mock_function_manager.execute_function.side_effect = ValueError("Unknown function")

    response = await async_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()
