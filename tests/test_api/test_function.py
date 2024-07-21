import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_register_function(async_client: AsyncClient, auth_headers):
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
    response = await async_client.post("/function/register", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    registered_function = response.json()
    assert registered_function["message"] == "Function registered successfully"
    assert "function_id" in registered_function
    return registered_function["function_id"]

async def test_get_function(async_client: AsyncClient, auth_headers, test_function):
    function_id = test_function
    response = await async_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    function = response.json()
    assert function["name"] == "test_function"
    assert function["description"] == "A test function"

async def test_update_function(async_client: AsyncClient, auth_headers, test_function):
    function_id = test_function
    update_data = {
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
    response = await async_client.put(f"/function/update", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_function = response.json()
    assert updated_function["message"] == "Function updated successfully"

async def test_delete_function(async_client: AsyncClient, auth_headers, test_function, test_agent):
    function_id = test_function
    response = await async_client.delete(f"/function/remove?agent_id={test_agent}&function_id={function_id}", headers=auth_headers)
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
    assert isinstance(functions["functions"], list)
    assert len(functions["functions"]) >= 2  # We should have at least the two functions we just registered

async def test_execute_function(async_client: AsyncClient, auth_headers, test_agent, test_function):
    execution_data = {
        "agent_id": test_agent,
        "function_name": "test_function",
        "parameters": {
            "param1": "test",
            "param2": 123
        }
    }
    response = await async_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
