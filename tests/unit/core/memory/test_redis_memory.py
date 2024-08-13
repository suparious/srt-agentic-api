import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.core.memory.redis.connection import RedisConnectionError
from app.api.models.memory import MemoryEntry, MemoryContext, AdvancedSearchQuery


@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()


@pytest.mark.asyncio
async def test_redis_memory_lifecycle(redis_memory):
    assert redis_memory.connection.redis is not None
    await redis_memory.close()
    assert redis_memory.connection.redis is None


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
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="Test content", max_results=3)
    results = await redis_memory.search(query)

    assert len(results) == 3
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


@pytest.mark.asyncio
async def test_redis_memory_error_handling(redis_memory):
    with patch.object(redis_memory.connection, 'get_connection', side_effect=RedisConnectionError("Connection failed")):
        with pytest.raises(RedisMemoryError):
            await redis_memory.add(MemoryEntry(
                content="Test error content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))


@pytest.mark.asyncio
async def test_redis_memory_initialization_error():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)

    with patch.object(redis_mem.connection, 'initialize', side_effect=RedisConnectionError("Initialization failed")):
        with pytest.raises(RedisMemoryError):
            await redis_mem.initialize()
