import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from app.core.memory.vector_memory import VectorMemory, VectorMemoryError
from app.api.models.memory import MemoryEntry, MemoryContext, AdvancedSearchQuery

@pytest.fixture
async def vector_memory():
    collection_name = f"test_collection_{UUID(int=0)}"
    vector_mem = VectorMemory(collection_name)
    await vector_mem.initialize()
    yield vector_mem
    await vector_mem.close()

@pytest.mark.asyncio
async def test_vector_memory_lifecycle(vector_memory):
    assert vector_memory.collection is not None
    await vector_memory.close()
    assert vector_memory.client is None

    await vector_memory.initialize()
    assert vector_memory.collection is not None

@pytest.mark.asyncio
async def test_vector_memory_add_and_get(vector_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await vector_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await vector_memory.get(memory_id)
    assert retrieved_entry is not None
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata

@pytest.mark.asyncio
async def test_vector_memory_search(vector_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await vector_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="Test content", max_results=3)
    results = await vector_memory.search(query)

    assert len(results) == 3
    assert all("Test content" in result["memory_entry"].content for result in results)

@pytest.mark.asyncio
async def test_vector_memory_delete(vector_memory):
    memory_entry = MemoryEntry(
        content="Test content to delete",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await vector_memory.add(memory_entry)

    await vector_memory.delete(memory_id)
    retrieved_entry = await vector_memory.get(memory_id)
    assert retrieved_entry is None

@pytest.mark.asyncio
async def test_vector_memory_get_recent(vector_memory):
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await vector_memory.add(memory_entry)

    recent_memories = await vector_memory.get_recent(5)
    assert len(recent_memories) == 5
    assert all("Test content" in memory["memory_entry"].content for memory in recent_memories)

@pytest.mark.asyncio
async def test_vector_memory_get_memories_older_than(vector_memory):
    now = datetime.now()
    threshold = now - timedelta(hours=2)

    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=now - timedelta(hours=i), metadata={})
        )
        await vector_memory.add(memory_entry)

    old_memories = await vector_memory.get_memories_older_than(threshold)
    assert len(old_memories) == 3
    assert all(memory.context.timestamp < threshold for memory in old_memories)

@pytest.mark.asyncio
async def test_vector_memory_cleanup(vector_memory):
    # Add some test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await vector_memory.add(memory_entry)

    # Perform cleanup
    await vector_memory.cleanup()

    # Verify that all data has been removed
    recent_memories = await vector_memory.get_recent(10)
    assert len(recent_memories) == 0

@pytest.mark.asyncio
async def test_vector_memory_error_handling(vector_memory):
    with patch.object(vector_memory.collection, 'add', side_effect=Exception("ChromaDB error")):
        with pytest.raises(VectorMemoryError):
            await vector_memory.add(MemoryEntry(
                content="Test error content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))

@pytest.mark.asyncio
async def test_vector_memory_search_with_filters(vector_memory):
    # Add test data with different context types and timestamps
    now = datetime.now()
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={"index": i},
            context=MemoryContext(
                context_type="type_A" if i % 2 == 0 else "type_B",
                timestamp=now - timedelta(hours=i),
                metadata={}
            )
        )
        await vector_memory.add(memory_entry)

    # Test search with context type filter
    query = AdvancedSearchQuery(query="Test content", context_type="type_A", max_results=5)
    results = await vector_memory.search(query)
    assert len(results) == 5
    assert all(result["memory_entry"].context.context_type == "type_A" for result in results)

    # Test search with time range filter
    time_range = {
        "start": now - timedelta(hours=5),
        "end": now
    }
    query = AdvancedSearchQuery(query="Test content", time_range=time_range, max_results=10)
    results = await vector_memory.search(query)
    assert len(results) == 6
    assert all(time_range["start"] <= result["memory_entry"].context.timestamp <= time_range["end"] for result in results)

    # Test search with metadata filter
    query = AdvancedSearchQuery(query="Test content", metadata_filters={"index": 3}, max_results=5)
    results = await vector_memory.search(query)
    assert len(results) == 1
    assert results[0]["memory_entry"].metadata["index"] == 3

@pytest.mark.asyncio
async def test_vector_memory_search_relevance(vector_memory):
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
        await vector_memory.add(memory_entry)

    query = AdvancedSearchQuery(query="quick brown fox", max_results=5)
    results = await vector_memory.search(query)

    assert len(results) == 5
    # Check if results are sorted by relevance
    relevance_scores = [result["relevance_score"] for result in results]
    assert relevance_scores == sorted(relevance_scores, reverse=True)
    # Check if the most relevant result is first
    assert "The quick brown fox" in results[0]["memory_entry"].content
