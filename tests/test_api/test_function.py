import pytest
from fastapi.testclient import TestClient

def test_register_function(test_client: TestClient, auth_headers):
    function_data = {
        "name": "test_function",
        "description": "A test function",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            }
        }
    }
    response = test_client.post("/function/", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    registered_function = response.json()
    assert registered_function["name"] == function_data["name"]
    return registered_function["id"]

def test_get_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    response = test_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    get_function = response.json()
    assert get_function["id"] == function_id

def test_update_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    update_data = {"description": "Updated test function"}
    response = test_client.patch(f"/function/{function_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_function = response.json()
    assert updated_function["description"] == update_data["description"]

def test_delete_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    response = test_client.delete(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 204

def test_list_functions(test_client: TestClient, auth_headers):
    response = test_client.get("/function/", headers=auth_headers)
    assert response.status_code == 200
    functions = response.json()
    assert isinstance(functions, list)
