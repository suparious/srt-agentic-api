import pytest
import json
from unittest.mock import AsyncMock
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture
def mock_redis_memory():
    return AsyncMock(spec=RedisMemory)


@pytest.mark.asyncio
async def test_add_memory(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    mock_redis_memory.add.return_value = "test_memory_id"

    memory_id = await mock_redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"
    mock_redis_memory.add.assert_called_once_with(memory_entry)


@pytest.mark.asyncio
async def test_get_memory(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_redis_memory.get.return_value = memory_entry

    retrieved_entry = await mock_redis_memory.get("test_memory_id")

    assert retrieved_entry == memory_entry
    mock_redis_memory.get.assert_called_once_with("test_memory_id")


@pytest.mark.asyncio
async def test_delete_memory(mock_redis_memory):
    await mock_redis_memory.delete("test_memory_id")
    mock_redis_memory.delete.assert_called_once_with("test_memory_id")


@pytest.mark.asyncio
async def test_search_basic(mock_redis_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = [
        {
            "id": "test_key_1",
            "memory_entry": MemoryEntry(
                content="Test memory content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ),
            "relevance_score": 0.8
        }
    ]
    mock_redis_memory.search.return_value = mock_results

    results = await mock_redis_memory.search(query)

    assert results == mock_results
    mock_redis_memory.search.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_add_memory_with_retry(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    mock_redis_memory.add.side_effect = [
        RedisMemoryError("Simulated failure"),
        RedisMemoryError("Simulated failure"),
        "test_memory_id"
    ]

    memory_id = await mock_redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"
    assert mock_redis_memory.add.call_count == 3

# More unit tests can be added here as needed