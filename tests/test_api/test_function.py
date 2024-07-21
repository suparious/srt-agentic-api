import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_function(test_client: AsyncClient, auth_headers):
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
    response = await test_client.post("/function/register", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    registered_function = response.json()
    assert registered_function["message"] == "Function registered successfully"
    assert "function_id" in registered_function
    return registered_function["function_id"]

@pytest.mark.asyncio
async def test_get_function(test_client: AsyncClient, auth_headers):
    function_id = await test_register_function(test_client, auth_headers)
    response = await test_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    function = response.json()
    assert function["name"] == "test_function"
    assert function["description"] == "A test function"

def test_update_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
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
    response = test_client.put(f"/function/update", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_function = response.json()
    assert updated_function["message"] == "Function updated successfully"

def test_delete_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    response = test_client.delete(f"/function/remove?agent_id=test_agent_id&function_id={function_id}", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Function removed successfully"

def test_list_functions(test_client: TestClient, auth_headers):
    # Register a couple of functions first
    test_register_function(test_client, auth_headers)
    test_register_function(test_client, auth_headers)

    response = test_client.get("/function/available?agent_id=test_agent_id", headers=auth_headers)
    assert response.status_code == 200
    functions = response.json()
    assert isinstance(functions["functions"], list)
    assert len(functions["functions"]) >= 2  # We should have at least the two functions we just registered

def test_execute_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    execution_data = {
        "agent_id": "test_agent_id",
        "function_name": "test_function",
        "parameters": {
            "param1": "test",
            "param2": 123
        }
    }
    response = test_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result