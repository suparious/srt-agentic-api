import pytest
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.api.models.memory import AdvancedSearchQuery
from app.core.models import MemoryEntry, MemoryContext

@pytest.fixture(scope="module")
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.cleanup()
    await redis_mem.close()

@pytest.mark.asyncio
async def test_redis_memory_lifecycle(redis_memory):
    assert redis_memory.connection.redis is not None
    await redis_memory.close()
    assert redis_memory.connection.redis is None
    await redis_memory.initialize()
    assert redis_memory.connection.redis is not None

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

    # Test basic search
    query = AdvancedSearchQuery(query="Test content", max_results=5)
    results = await redis_memory.search(query)
    assert len(results) == 5
    assert all("Test content" in result["memory_entry"].content for result in results)

    # Test search with context type filter
    query = AdvancedSearchQuery(query="Test content", context_type="test", max_results=5)
    results = await redis_memory.search(query)
    assert len(results) == 5
    assert all(result["memory_entry"].context.context_type == "test" for result in results)

    # Test search with time range filter
    time_range = {
        "start": datetime.now() - timedelta(minutes=6),
        "end": datetime.now()
    }
    query = AdvancedSearchQuery(query="Test content", time_range=time_range, max_results=10)
    results = await redis_memory.search(query)
    assert len(results) == 6
    assert all(time_range["start"] <= result["memory_entry"].context.timestamp <= time_range["end"] for result in results)

    # Test search with metadata filter
    query = AdvancedSearchQuery(query="Test content", metadata_filters={"index": 3}, max_results=5)
    results = await redis_memory.search(query)
    assert len(results) == 1
    assert results[0]["memory_entry"].metadata["index"] == 3

    # Test search with no results
    query = AdvancedSearchQuery(query="Nonexistent content", max_results=5)
    results = await redis_memory.search(query)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_redis_memory_search_relevance(redis_memory):
    # Add test data with varying relevance
    entries = [
        "The quick brown fox jumps over the lazy dog",
        "A quick brown dog jumps over the lazy fox",
        "The lazy dog sleeps while the quick fox jumps",
        "A brown fox quickly jumps over a dog",
        "The dog is lazy and the fox is quick"
    ]
    for entry in entries:
        memory_entry = MemoryEntry(
            content=entry,
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="quick brown fox", max_results=5)
    results = await redis_memory.search(query)

    assert len(results) == 5
    # Check if results are sorted by relevance
    relevance_scores = [result["relevance_score"] for result in results]
    assert relevance_scores == sorted(relevance_scores, reverse=True)
    # Check if the most relevant result is first
    assert "The quick brown fox" in results[0]["memory_entry"].content

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
async def test_redis_memory_cleanup(redis_memory):
    memory_entry = MemoryEntry(
        content="Test cleanup content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    await redis_memory.add(memory_entry)

    await redis_memory.cleanup()

    recent_memories = await redis_memory.get_recent(10)
    assert len(recent_memories) == 0
