import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock
from app.core.memory.vector_memory import VectorMemory, VectorMemoryError
from app.api.models.memory import AdvancedSearchQuery
from app.core.models import MemoryEntry, MemoryContext

@pytest.fixture
async def vector_memory():
    collection_name = f"test_collection_{UUID(int=0)}"
    vector_mem = VectorMemory(collection_name)
    await vector_mem.initialize()
    yield vector_mem
    await vector_mem.close()

@pytest.mark.asyncio
async def test_vector_memory_lifecycle(vector_memory):
    # Test initialization and closure
    assert vector_memory.collection is not None
    await vector_memory.close()
    assert vector_memory.client is None

    # Test reinitialization
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
async def test_vector_memory_error_handling(vector_memory):
    with patch.object(vector_memory.collection, 'add', side_effect=Exception("ChromaDB error")):
        with pytest.raises(VectorMemoryError):
            await vector_memory.add(MemoryEntry(
                content="Test error content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ))
