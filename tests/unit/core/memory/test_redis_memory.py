import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.redis.connection import RedisConnectionError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType
from app.utils.logging import memory_logger


@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()


@pytest.mark.asyncio
async def test_redis_connection_lifecycle():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)

    # Test initialization
    assert redis_mem.redis is None

    # Test connection establishment
    await redis_mem.initialize()
    assert redis_mem.redis is not None

    # Test connection usage
    async with redis_mem.get_connection() as conn:
        await conn.set("test_key", "test_value")
        value = await conn.get("test_key")
        assert value == "test_value"

    # Test connection closure
    await redis_mem.close()
    assert redis_mem.redis is None

    # Test error handling when trying to use a closed connection
    with pytest.raises(RedisMemoryError):
        async with redis_mem.get_connection():
            pass


@pytest.mark.asyncio
async def test_add_memory(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    # Verify the memory was added correctly
    async with redis_memory.get_connection() as conn:
        value = await conn.get(f"agent:{redis_memory.agent_id}:{memory_id}")
        assert value is not None
        deserialized = json.loads(value)
        assert deserialized["content"] == memory_entry.content
        assert deserialized["metadata"] == memory_entry.metadata


@pytest.mark.asyncio
async def test_get_memory(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add(memory_entry)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata
    assert retrieved_entry.context.context_type == memory_entry.context.context_type


@pytest.mark.asyncio
async def test_delete_memory(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory to delete",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add(memory_entry)

    await redis_memory.delete(memory_id)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is None


@pytest.mark.asyncio
async def test_search_basic(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="Test memory", max_results=3)
    results = await redis_memory.search(query)

    assert len(results) == 3
    assert all("Test memory" in result["memory_entry"].content for result in results)


@pytest.mark.asyncio
async def test_get_recent_memories(redis_memory):
    # Add test data
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test memory {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    recent_memories = await redis_memory.get_recent(5)
    assert len(recent_memories) == 5
    assert all("Test memory" in memory["memory_entry"].content for memory in recent_memories)

    # Check if memories are in reverse chronological order
    timestamps = [memory["timestamp"] for memory in recent_memories]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_memories_older_than(redis_memory):
    now = datetime.now()
    threshold = now - timedelta(hours=2)

    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Old memory {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="old_test", timestamp=now - timedelta(hours=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    old_memories = await redis_memory.get_memories_older_than(threshold)

    assert len(old_memories) == 3
    assert all(memory.context.timestamp < threshold for memory in old_memories)


@pytest.mark.asyncio
async def test_connection_manager():
    manager = RedisConnectionManager.get_instance()
    pool1 = await manager.get_pool("redis://localhost:6379/0")
    pool2 = await manager.get_pool("redis://localhost:6379/0")
    assert pool1 is pool2

    pool3 = await manager.get_pool("redis://localhost:6379/1")
    assert pool1 is not pool3

    await manager.close_all()


@pytest.mark.asyncio
async def test_cleanup():
    agent_id1 = UUID('11111111-1111-1111-1111-111111111111')
    agent_id2 = UUID('22222222-2222-2222-2222-222222222222')

    redis_mem1 = RedisMemory(agent_id1)
    redis_mem2 = RedisMemory(agent_id2)

    await redis_mem1.initialize()
    await redis_mem2.initialize()

    await RedisMemory.cleanup()

    # Verify that connections are closed
    with pytest.raises(RedisMemoryError):
        async with redis_mem1.get_connection() as conn:
            await conn.ping()

    with pytest.raises(RedisMemoryError):
        async with redis_mem2.get_connection() as conn:
            await conn.ping()
