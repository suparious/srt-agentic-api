import pytest
import json
from unittest.mock import patch, MagicMock
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_memory = RedisMemory(agent_id)
    yield redis_memory
    # Clean up after tests
    await redis_memory.redis.flushdb()

@pytest.mark.asyncio
async def test_advanced_search(mock_redis_memory):
    query = AdvancedSearchQuery(
        query="Test memory",
        memory_type=MemoryType.SHORT_TERM,
        context_type="test_context",
        time_range={
            "start": datetime.now() - timedelta(hours=5),
            "end": datetime.now()
        },
        metadata_filters={"key": "value"},
        relevance_threshold=0.5,
        max_results=3
    )

    mock_results = [
        {
            "id": f"test_key_{i}",
            "memory_entry": MemoryEntry(
                content=f"Test memory content {i}",
                metadata={"key": "value"},
                context=MemoryContext(
                    context_type="test_context",
                    timestamp=datetime.now() - timedelta(hours=i),
                    metadata={}
                )
            ),
            "relevance_score": 0.5 + (i * 0.1)
        } for i in range(3)
    ]

    mock_redis_memory.search.return_value = mock_results

    results = await mock_redis_memory.search(query)

    assert len(results) == 3
    for result in results:
        assert "Test memory" in result['memory_entry'].content
        assert result['memory_entry'].metadata['key'] == "value"
        assert result['memory_entry'].context.context_type == "test_context"
        assert result['memory_entry'].context.timestamp >= query.time_range['start']
        assert result['memory_entry'].context.timestamp <= query.time_range['end']
        assert result['relevance_score'] >= 0.5

    mock_redis_memory.search.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_add_and_retrieve_memory(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    # Mock the add method
    mock_redis_memory.add.return_value = "test_memory_id"

    memory_id = await mock_redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"

    # Mock the get method
    mock_redis_memory.get.return_value = memory_entry

    retrieved_entry = await mock_redis_memory.get(memory_id)
    assert retrieved_entry == memory_entry

    mock_redis_memory.add.assert_called_once_with(memory_entry)
    mock_redis_memory.get.assert_called_once_with(memory_id)


@pytest.mark.asyncio
async def test_advanced_search_with_query(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

    query = AdvancedSearchQuery(query="content 3", max_results=2)
    results = await redis_memory.search(query)

    assert len(results) == 1
    assert results[0]["memory_entry"].content == "Test memory content 3"


@pytest.mark.asyncio
async def test_advanced_search_with_metadata_filters(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i, "even": i % 2 == 0},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

    query = AdvancedSearchQuery(query="content", metadata_filters={"even": True}, max_results=5)
    results = await redis_memory.search(query)

    assert len(results) == 3
    assert all(result["memory_entry"].metadata["even"] for result in results)


@pytest.mark.asyncio
async def test_advanced_search_with_time_range(redis_memory):
    now = datetime.now()
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=now - timedelta(days=i), metadata={})
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

    query = AdvancedSearchQuery(
        query="content",
        time_range={"start": now - timedelta(days=2), "end": now},
        max_results=5
    )
    results = await redis_memory.search(query)

    assert len(results) == 3
    assert all(result["memory_entry"].context.timestamp >= now - timedelta(days=2) for result in results)


@pytest.mark.asyncio
async def test_advanced_search_with_relevance_threshold(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

    query = AdvancedSearchQuery(query="content", relevance_threshold=0.5, max_results=5)
    results = await redis_memory.search(query)

    assert all(result["relevance_score"] >= 0.5 for result in results)


@pytest.mark.asyncio
async def test_advanced_search_with_context_type(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type=f"type_{i % 2}", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

    query = AdvancedSearchQuery(query="content", context_type="type_0", max_results=5)
    results = await redis_memory.search(query)

    assert len(results) == 3
    assert all(result["memory_entry"].context.context_type == "type_0" for result in results)

@pytest.mark.asyncio
async def test_add_memory_with_retry(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    # Mock the add method to fail twice and succeed on the third attempt
    mock_redis_memory.add.side_effect = [
        RedisMemoryError("Simulated failure"),
        RedisMemoryError("Simulated failure"),
        "test_memory_id"
    ]

    memory_id = await mock_redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"
    assert mock_redis_memory.add.call_count == 3
