import pytest
import asyncio
from uuid import UUID
from typing import List
from datetime import datetime, timedelta
from unittest.mock import patch
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.core.memory.redis.connection import RedisConnectionError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext
from app.utils.logging import memory_logger


@pytest.fixture(scope="module")
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.cleanup()


@pytest.mark.asyncio
async def test_add_and_retrieve_memory_integration(redis_memory: RedisMemory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata
    assert retrieved_entry.context.context_type == memory_entry.context.context_type


@pytest.mark.asyncio
async def test_redis_connection_lifecycle():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)

    # Test initialization
    assert redis_mem.connection.redis is None

    # Test connection establishment
    await redis_mem.initialize()
    assert redis_mem.connection.redis is not None
    assert redis_mem.connection.redis.connection_pool is not None

    # Test connection usage
    async with redis_mem.connection.get_connection() as conn:
        await conn.set("test_key", "test_value")
        value = await conn.get("test_key")
        assert value == "test_value"

    # Test connection closure
    await redis_mem.close()
    assert redis_mem.connection.redis is None

    # Test error handling when trying to use a closed connection
    with pytest.raises(RedisConnectionError):
        async with redis_mem.connection.get_connection():
            pass

    # Clean up
    await redis_mem.initialize()
    async with redis_mem.connection.get_connection() as conn:
        await conn.delete("test_key")
    await redis_mem.close()


@pytest.mark.asyncio
async def test_advanced_search_integration(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i, "even": i % 2 == 0},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(days=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(
        query="content",
        metadata_filters={"even": True},
        time_range={"start": datetime.now() - timedelta(days=4), "end": datetime.now()},
        max_results=3
    )

    results = await redis_memory.search(query)

    assert len(results) <= 3
    assert all(result["memory_entry"].metadata["even"] for result in results)
    assert all(
        datetime.now() - timedelta(days=4) <= result["memory_entry"].context.timestamp <= datetime.now() for result in
        results)


@pytest.mark.asyncio
async def test_delete_memory_integration(redis_memory):
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
async def test_get_recent_memories_integration(redis_memory):
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test memory {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    recent_memories = await redis_memory.get_recent(5)
    assert len(recent_memories) == 5
    assert all(memory["memory_entry"].content.startswith("Test memory") for memory in recent_memories)

    # Check if memories are in reverse chronological order
    timestamps = [memory["timestamp"] for memory in recent_memories]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def get_memories_older_than(self, threshold: datetime) -> List[MemoryEntry]:
    pattern = f"agent:{self.agent_id}:*"
    old_memories = []

    async with self.get_connection() as conn:
        cursor = 0
        while True:
            cursor, keys = await conn.scan(cursor, match=pattern, count=100)
            pipeline = conn.pipeline()
            for key in keys:
                pipeline.get(key)
            values = await pipeline.execute()

            for value in values:
                if value:
                    memory_entry = MemoryEntry.model_validate_json(value)
                    if memory_entry.context.timestamp < threshold:
                        old_memories.append(memory_entry)

            if cursor == 0:
                break

    memory_logger.info(
        f"Retrieved {len(old_memories)} memories older than {threshold} for agent: {self.agent_id}"
    )
    return old_memories


@pytest.mark.asyncio
async def test_get_memories_older_than_integration(redis_memory):
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

    assert len(old_memories) == 3, f"Expected 3 memories, but got {len(old_memories)}"
    assert all(memory.context.timestamp < threshold for memory in old_memories)

    # Log details for debugging
    memory_logger.info(f"Threshold: {threshold}")
    for memory in old_memories:
        memory_logger.info(f"Memory timestamp: {memory.context.timestamp}, Content: {memory.content}")


@pytest.mark.asyncio
async def test_redis_memory_connection_error_handling():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)

    # Test initialization failure
    with patch.object(redis_mem.connection, 'initialize', side_effect=RedisConnectionError("Connection failed")):
        with pytest.raises(RedisMemoryError):
            await redis_mem.initialize()

    # Test operation failure due to connection error
    await redis_mem.initialize()
    with patch.object(redis_mem.connection, 'get_connection', side_effect=RedisConnectionError("Connection lost")):
        with pytest.raises(RedisMemoryError):
            async with redis_mem.get_connection() as conn:
                await conn.set("test_key", "test_value")

    # Test successful reconnection after failure
    with patch.object(redis_mem.connection, 'initialize') as mock_initialize:
        await redis_mem.initialize()
        mock_initialize.assert_called_once()

    await redis_mem.close()


@pytest.mark.asyncio
async def test_redis_memory_concurrent_access():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()

    async def concurrent_operation(key, value):
        async with redis_mem.get_connection() as conn:
            await conn.set(key, value)
            return await conn.get(key)

    tasks = [concurrent_operation(f"key_{i}", f"value_{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)

    assert results == ["value_0", "value_1", "value_2", "value_3", "value_4"]

    await redis_mem.close()
