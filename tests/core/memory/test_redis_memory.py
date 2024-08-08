import pytest
import json
from unittest.mock import patch, MagicMock
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_memory = RedisMemory(agent_id)
    yield redis_memory
    # Clean up after tests
    await redis_memory.redis.flushdb()

@pytest.mark.asyncio
async def test_advanced_search(redis_memory):
    # Add test data
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"key": "value" if i % 2 == 0 else "other"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now() - timedelta(hours=i),
                metadata={}
            )
        )
        await redis_memory.add(f"test_key_{i}", memory_entry)

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

    results = await redis_memory.search(query)

    assert len(results) == 3
    for result in results:
        assert "Test memory" in result['memory_entry'].content
        assert result['memory_entry'].metadata['key'] == "value"
        assert result['memory_entry'].context.context_type == "test_context"
        assert result['memory_entry'].context.timestamp >= query.time_range['start']
        assert result['memory_entry'].context.timestamp <= query.time_range['end']
        assert result['relevance_score'] >= 0.5

@pytest.mark.asyncio
async def test_add_and_retrieve_memory(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add("test_key", memory_entry)
    retrieved_entry = await redis_memory.get("test_key")
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata
    assert retrieved_entry.context.context_type == memory_entry.context.context_type


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
async def test_add_memory_with_retry(redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    # Mock the Redis connection to simulate failures
    with patch('app.core.memory.redis_memory.Redis') as mock_redis:
        mock_conn = MagicMock()
        mock_conn.set.side_effect = [
            RedisMemoryError("Simulated failure"),
            RedisMemoryError("Simulated failure"),
            None  # Success on third attempt
        ]
        mock_redis.return_value = mock_conn

        memory_id = await redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert mock_conn.set.call_count == 3  # Verify that it retried twice before succeeding

    # Verify the memory was added correctly
    with patch('app.core.memory.redis_memory.Redis') as mock_redis:
        mock_conn = MagicMock()
        mock_conn.get.return_value = json.dumps({
            "content": memory_entry.content,
            "metadata": memory_entry.metadata,
            "context": {
                "context_type": memory_entry.context.context_type,
                "timestamp": memory_entry.context.timestamp.isoformat(),
                "metadata": memory_entry.context.metadata
            }
        })
        mock_redis.return_value = mock_conn

        retrieved_entry = await redis_memory.get(memory_id)

    assert retrieved_entry == memory_entry
