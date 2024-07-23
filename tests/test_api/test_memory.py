import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.memory import MemoryType, MemoryOperation

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_add_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_data = {
        "agent_id": await test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "entry": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert added_memory["message"] == "Memory added successfully"
    assert "memory_id" in added_memory
    return added_memory["memory_id"]

@pytest.mark.asyncio
async def test_retrieve_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    retrieve_data = {
        "agent_id": await test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "memory_id": memory_id
    }
    response = await async_client.get("/memory/retrieve", params=retrieve_data, headers=auth_headers)
    assert response.status_code == 200
    memory = response.json()
    assert memory["content"] == "Test memory content"
    assert memory["metadata"] == {"key": "value"}

async def test_search_memory(async_client: AsyncClient, auth_headers, test_agent):
    await test_add_memory(async_client, auth_headers, test_agent)  # Add a memory to search for
    search_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "query": "Test memory",
        "limit": 5
    }
    response = await async_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0

async def test_delete_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    delete_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "memory_id": memory_id
    }
    response = await async_client.delete("/memory/delete", params=delete_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Memory deleted successfully"

async def test_memory_operation(async_client: AsyncClient, auth_headers, test_agent):
    operation_data = {
        "agent_id": test_agent,
        "operation": MemoryOperation.ADD,
        "memory_type": MemoryType.SHORT_TERM,
        "data": {
            "content": "Test operation memory content",
            "metadata": {"operation": "test"}
        }
    }
    response = await async_client.post("/memory/operate", json=operation_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "ADD operation completed successfully"
    assert "result" in result
