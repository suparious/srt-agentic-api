import pytest
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture(scope="module")
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.cleanup()


@pytest.mark.asyncio
async def test_add_and_retrieve_memory_integration(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    try:
        memory_id = await redis_memory.add(memory_entry)
        assert isinstance(memory_id, str)

        retrieved_entry = await redis_memory.get(memory_id)
        assert retrieved_entry is not None
        assert retrieved_entry.content == memory_entry.content
        assert retrieved_entry.metadata == memory_entry.metadata
        assert retrieved_entry.context.context_type == memory_entry.context.context_type
    except RedisMemoryError as e:
        pytest.fail(f"Redis memory operation failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {str(e)}")


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

    assert len(old_memories) == 3
    assert all(memory.context.timestamp < threshold for memory in old_memories)
