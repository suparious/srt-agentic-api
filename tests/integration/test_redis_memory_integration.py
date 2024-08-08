import pytest
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.mark.asyncio
async def test_add_and_retrieve_memory_integration(redis_memory):
    memory_entry = MemoryEntry(
        content="Integration test memory content",
        metadata={"key": "integration_value"},
        context=MemoryContext(context_type="integration_test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry == memory_entry


@pytest.mark.asyncio
async def test_advanced_search_integration(redis_memory):
    # Add test data
    now = datetime.now()
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Integration test memory content {i}",
            metadata={"key": "value" if i % 2 == 0 else "other"},
            context=MemoryContext(
                context_type="integration_test_context",
                timestamp=now - timedelta(hours=i),
                metadata={}
            )
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(
        query="Integration test memory",
        memory_type=MemoryType.SHORT_TERM,
        context_type="integration_test_context",
        time_range={
            "start": now - timedelta(hours=5),
            "end": now
        },
        metadata_filters={"key": "value"},
        relevance_threshold=0.5,
        max_results=3
    )

    results = await redis_memory.search(query)

    assert len(results) <= 3
    for result in results:
        assert "Integration test memory" in result['memory_entry'].content
        assert result['memory_entry'].metadata['key'] == "value"
        assert result['memory_entry'].context.context_type == "integration_test_context"
        assert result['memory_entry'].context.timestamp >= query.time_range['start']
        assert result['memory_entry'].context.timestamp <= query.time_range['end']
        assert result['relevance_score'] >= 0.5


@pytest.mark.asyncio
async def test_delete_memory_integration(redis_memory):
    memory_entry = MemoryEntry(
        content="Memory to be deleted",
        metadata={"key": "delete_test"},
        context=MemoryContext(context_type="delete_test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)

    # Verify the memory was added
    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry == memory_entry

    # Delete the memory
    await redis_memory.delete(memory_id)

    # Verify the memory was deleted
    deleted_entry = await redis_memory.get(memory_id)
    assert deleted_entry is None


@pytest.mark.asyncio
async def test_get_recent_memories_integration(redis_memory):
    # Add test data
    now = datetime.now()
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Recent memory {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="recent_test", timestamp=now - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    recent_memories = await redis_memory.get_recent(3)

    assert len(recent_memories) == 3
    assert [mem['memory_entry'].content for mem in recent_memories] == ["Recent memory 0", "Recent memory 1",
                                                                        "Recent memory 2"]


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
    for memory in old_memories:
        assert memory.context.timestamp < threshold
