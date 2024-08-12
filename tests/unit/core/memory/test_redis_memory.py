import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.core.memory.redis.connection import RedisConnectionError
from app.api.models.memory import MemoryEntry, MemoryContext

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
    assert redis_mem.connection.redis is None

    # Test connection establishment
    await redis_mem.initialize()
    assert redis_mem.connection.redis is not None
    assert redis_mem.connection._connection_pool is not None

    # Test connection usage
    async with redis_mem.connection.get_connection() as conn:
        await conn.set("test_key", "test_value")
        value = await conn.get("test_key")
        assert value == "test_value"

    # Test connection closure
    await redis_mem.close()
    assert redis_mem.connection.redis is None
    assert redis_mem.connection._connection_pool is None

    # Test error handling when trying to use a closed connection
    with pytest.raises(RedisConnectionError):
        async with redis_mem.connection.get_connection():
            pass

    # Test reinitialization after closure
    await redis_mem.initialize()
    assert redis_mem.connection.redis is not None
    assert redis_mem.connection._connection_pool is not None

    # Clean up
    await redis_mem.close()

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
    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata

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
async def test_search_memory(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = {"query": "Test memory", "max_results": 3}
    results = await redis_memory.search(query)

    assert len(results) == 3
    assert all("Test memory" in result["content"] for result in results)

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
    assert all("Test memory" in memory["content"] for memory in recent_memories)

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
async def test_redis_cleanup():
    with patch('app.core.memory.redis_memory.RedisCleanup') as mock_cleanup:
        await RedisMemory.cleanup()
        mock_cleanup.return_value.cleanup.assert_called_once()

@pytest.mark.asyncio
async def test_error_handling(redis_memory):
    with patch.object(redis_memory.operations, 'add', side_effect=Exception("Test error")):
        with pytest.raises(RedisMemoryError):
            await redis_memory.add(MemoryEntry(
                content="Test error memory",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))

@pytest.mark.asyncio
async def test_connection_error_handling(redis_memory):
    with patch.object(redis_memory.connection, 'ensure_connection', side_effect=RedisConnectionError("Connection failed")):
        with pytest.raises(RedisMemoryError):
            await redis_memory.add(MemoryEntry(
                content="Test connection error",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))

@pytest.mark.asyncio
async def test_reconnection_after_error(redis_memory):
    # Simulate a connection error
    with patch.object(redis_memory.connection, 'ensure_connection', side_effect=RedisConnectionError("Connection failed")):
        with pytest.raises(RedisMemoryError):
            await redis_memory.add(MemoryEntry(
                content="Test reconnection",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))

    # Now try to use the connection again, it should reconnect automatically
    memory_entry = MemoryEntry(
        content="Test reconnection successful",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == "Test reconnection successful"
