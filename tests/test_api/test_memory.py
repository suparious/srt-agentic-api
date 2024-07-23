import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.memory import MemoryType, MemoryOperation

pytestmark = pytest.mark.asyncio

async def test_add_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "entry": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert "memory_id" in added_memory
    assert added_memory["message"] == "Memory added successfully"
    return added_memory["memory_id"]

async def test_retrieve_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    response = await async_client.get(f"/memory/retrieve?agent_id={test_agent}&memory_type={MemoryType.SHORT_TERM}&memory_id={memory_id}", headers=auth_headers)
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
    assert "results" in results
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0

async def test_delete_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    response = await async_client.delete(f"/memory/delete?agent_id={test_agent}&memory_type={MemoryType.SHORT_TERM}&memory_id={memory_id}", headers=auth_headers)
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

async def test_add_long_term_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.LONG_TERM,
        "entry": {
            "content": "Long-term test memory content",
            "metadata": {"key": "long_term_value"}
        }
    }
    response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert "memory_id" in added_memory
    assert added_memory["message"] == "Memory added successfully"

async def test_search_long_term_memory(async_client: AsyncClient, auth_headers, test_agent):
    await test_add_long_term_memory(async_client, auth_headers, test_agent)
    search_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.LONG_TERM,
        "query": "Long-term test",
        "limit": 5
    }
    response = await async_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert "results" in results
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0
    assert "Long-term test memory content" in results["results"][0]["content"]
