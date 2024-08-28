import pytest
import asyncio
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.core.memory.redis.connection import RedisConnectionError
from app.api.models.memory import AdvancedSearchQuery
from app.core.models import MemoryEntry, MemoryContext
@pytest.mark.asyncio
async def test_redis_memory_lifecycle():
    with patch('app.core.memory.redis.connection.Redis') as MockRedis:
        # Set up the mock
        mock_redis = AsyncMock()
        MockRedis.from_url.return_value = mock_redis

        # Test successful initialization
        redis_memory = RedisMemory(agent_id='test-agent')
        await redis_memory.initialize()
        assert redis_memory.connection.redis is not None
        mock_redis.ping.assert_called_once()

        # Test successful close
        await redis_memory.close()
        assert redis_memory.connection.redis is None
        mock_redis.close.assert_called_once()

        # Test re-initialization
        await redis_memory.initialize()
        assert redis_memory.connection.redis is not None
        assert mock_redis.ping.call_count == 2

        # Test initialization failure
        mock_redis.ping.side_effect = RedisConnectionError("Connection failed")
        with pytest.raises(RedisMemoryError):
            await redis_memory.initialize()

        # Test cleanup
        mock_redis.ping.side_effect = None  # Reset side effect
        await redis_memory.cleanup()
        # Add assertions for cleanup operations

        # Test operation after cleanup
        with pytest.raises(RedisMemoryError):
            await redis_memory.add(AsyncMock())  # This should fail as the connection is closed

        # Test reconnection after failure
        mock_redis.ping.side_effect = None  # Reset side effect
        await redis_memory.initialize()
        assert redis_memory.connection.redis is not None

        # Test concurrent operations
        async def concurrent_operation():
            await redis_memory.add(AsyncMock())

        await asyncio.gather(*[concurrent_operation() for _ in range(10)])
        assert mock_redis.set.call_count == 10

@pytest.mark.asyncio
async def test_redis_memory_add_and_get(redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata

@pytest.mark.asyncio
async def test_redis_memory_search(redis_memory):
    # Add test data
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="Test content", max_results=5)
    results = await redis_memory.search(query)
    assert len(results) == 5
    assert all("Test content" in result["memory_entry"].content for result in results)

@pytest.mark.asyncio
async def test_redis_memory_delete(redis_memory):
    memory_entry = MemoryEntry(
        content="Test content to delete",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add(memory_entry)

    await redis_memory.delete(memory_id)
    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is None

@pytest.mark.asyncio
async def test_redis_memory_get_recent(redis_memory):
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    recent_memories = await redis_memory.get_recent(5)
    assert len(recent_memories) == 5
    assert all("Test content" in memory["memory_entry"].content for memory in recent_memories)

@pytest.mark.asyncio
async def test_redis_memory_get_memories_older_than(redis_memory):
    now = datetime.now()
    threshold = now - timedelta(hours=2)

    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=now - timedelta(hours=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    old_memories = await redis_memory.get_memories_older_than(threshold)
    assert len(old_memories) == 3
    assert all(memory.context.timestamp < threshold for memory in old_memories)
