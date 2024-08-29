import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from app.core.memory.memory_system import MemorySystem, MemorySystemError
from app.api.models.memory import AdvancedSearchQuery, MemoryType
from app.core.models import MemoryEntry, MemoryContext, MemoryConfig


@pytest.fixture
def memory_config():
    return MemoryConfig(use_redis_cache=True, use_long_term_memory=True)


@pytest.fixture
async def memory_system(memory_config):
    system = MemorySystem(agent_id='12345678-1234-5678-1234-567812345678', config=memory_config)
    await system.initialize()
    yield system
    await system.close()


@pytest.mark.asyncio
async def test_memory_system_initialization(memory_config):
    with patch('app.core.memory.memory_system.RedisMemory') as MockRedisMemory, \
            patch('app.core.memory.memory_system.VectorMemory') as MockVectorMemory:
        mock_redis = AsyncMock()
        mock_vector = AsyncMock()
        MockRedisMemory.return_value = mock_redis
        MockVectorMemory.return_value = mock_vector

        system = MemorySystem(agent_id='test-agent', config=memory_config)
        await system.initialize()

        MockRedisMemory.assert_called_once_with('test-agent')
        MockVectorMemory.assert_called_once_with('test-agent')
        mock_redis.initialize.assert_called_once()
        mock_vector.initialize.assert_called_once()


@pytest.mark.asyncio
async def test_add_short_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("SHORT_TERM", memory_entry)
    assert isinstance(memory_id, str)
    assert len(memory_system.consolidation_queue) == 1


@pytest.mark.asyncio
async def test_add_long_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("LONG_TERM", memory_entry)
    assert isinstance(memory_id, str)


@pytest.mark.asyncio
async def test_retrieve_short_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("SHORT_TERM", memory_entry)
    retrieved_memory = await memory_system.retrieve("SHORT_TERM", memory_id)
    assert retrieved_memory.content == memory_entry.content


@pytest.mark.asyncio
async def test_retrieve_long_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("LONG_TERM", memory_entry)
    retrieved_memory = await memory_system.retrieve("LONG_TERM", memory_id)
    assert retrieved_memory.content == memory_entry.content


@pytest.mark.asyncio
async def test_search(memory_system):
    # Add some test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        )
        await memory_system.add("SHORT_TERM", memory_entry)
        await memory_system.add("LONG_TERM", memory_entry)

    query = AdvancedSearchQuery(query="Test content", max_results=3)
    results = await memory_system.search(query)
    assert len(results) == 3
    assert all("Test content" in result["memory_entry"].content for result in results)


@pytest.mark.asyncio
async def test_delete_short_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("SHORT_TERM", memory_entry)
    await memory_system.delete("SHORT_TERM", memory_id)
    retrieved_memory = await memory_system.retrieve("SHORT_TERM", memory_id)
    assert retrieved_memory is None


@pytest.mark.asyncio
async def test_delete_long_term_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    memory_id = await memory_system.add("LONG_TERM", memory_entry)
    await memory_system.delete("LONG_TERM", memory_id)
    retrieved_memory = await memory_system.retrieve("LONG_TERM", memory_id)
    assert retrieved_memory is None


@pytest.mark.asyncio
async def test_perform_operation_add(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    result = await memory_system.perform_operation("ADD", "SHORT_TERM", memory_entry.dict())
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_consolidate_memories(memory_system):
    # Add some old memories to short-term storage
    old_time = datetime.now() - timedelta(hours=2)
    for i in range(3):
        memory_entry = MemoryEntry(
            content=f"Old content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=old_time, metadata={})
        )
        await memory_system.add("SHORT_TERM", memory_entry)

    await memory_system.consolidate_memories()

    # Check that memories have been moved to long-term storage
    query = AdvancedSearchQuery(query="Old content", max_results=5)
    results = await memory_system.search(query)
    assert len(results) == 3
    assert all(result["memory_entry"].context.timestamp == old_time for result in results)


@pytest.mark.asyncio
async def test_forget_old_memories(memory_system):
    # Add some very old memories to long-term storage
    very_old_time = datetime.now() - timedelta(days=31)
    for i in range(3):
        memory_entry = MemoryEntry(
            content=f"Very old content {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=very_old_time, metadata={})
        )
        await memory_system.add("LONG_TERM", memory_entry)

    await memory_system.forget_old_memories(timedelta(days=30))

    # Check that old memories have been forgotten
    query = AdvancedSearchQuery(query="Very old content", max_results=5)
    results = await memory_system.search(query)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_memory_system_error_handling(memory_system):
    with pytest.raises(MemorySystemError):
        await memory_system.add("INVALID_TYPE", MemoryEntry(
            content="Test content",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
        ))

    with pytest.raises(MemorySystemError):
        await memory_system.retrieve("INVALID_TYPE", "some_id")

    with pytest.raises(MemorySystemError):
        await memory_system.delete("INVALID_TYPE", "some_id")

    with pytest.raises(MemorySystemError):
        await memory_system.perform_operation("INVALID_OPERATION", "SHORT_TERM", {})


@pytest.mark.asyncio
async def test_memory_system_close(memory_config):
    with patch('app.core.memory.memory_system.RedisMemory') as MockRedisMemory, \
            patch('app.core.memory.memory_system.VectorMemory') as MockVectorMemory:
        mock_redis = AsyncMock()
        mock_vector = AsyncMock()
        MockRedisMemory.return_value = mock_redis
        MockVectorMemory.return_value = mock_vector

        system = MemorySystem(agent_id='test-agent', config=memory_config)
        await system.initialize()
        await system.close()

        mock_redis.close.assert_called_once()
        mock_vector.close.assert_called_once()


@pytest.mark.asyncio
async def test_memory_system_search_with_errors(memory_system):
    # Mock the search methods to simulate errors
    memory_system.short_term.search = AsyncMock(side_effect=Exception("Short-term search error"))
    memory_system.long_term.search = AsyncMock(side_effect=Exception("Long-term search error"))

    query = AdvancedSearchQuery(query="Test content", max_results=3)
    results = await memory_system.search(query)

    # Both searches failed, so results should be empty
    assert len(results) == 0

    # Check that errors were logged
    memory_system.short_term.search.assert_called_once()
    memory_system.long_term.search.assert_called_once()


@pytest.mark.asyncio
async def test_memory_system_partial_search_success(memory_system):
    # Mock the search methods to simulate partial success
    memory_system.short_term.search = AsyncMock(return_value=[
        {"memory_entry": MemoryEntry(content="Short-term content", metadata={},
                                     context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})),
         "relevance_score": 0.8}
    ])
    memory_system.long_term.search = AsyncMock(side_effect=Exception("Long-term search error"))

    query = AdvancedSearchQuery(query="Test content", max_results=3)
    results = await memory_system.search(query)

    # Short-term search succeeded, long-term failed
    assert len(results) == 1
    assert results[0]["memory_entry"].content == "Short-term content"

    memory_system.short_term.search.assert_called_once()
    memory_system.long_term.search.assert_called_once()

@pytest.mark.asyncio
async def test_add_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test",
            timestamp=datetime.now(),
            metadata={}
        )
    )
    memory_id = await memory_system.add(MemoryType.SHORT_TERM, memory_entry)
    assert isinstance(memory_id, str)
    retrieved_memory = await memory_system.retrieve(MemoryType.SHORT_TERM, memory_id)
    assert retrieved_memory.content == "Test memory content"

@pytest.mark.asyncio
async def test_retrieve_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now())
    )
    memory_id = await memory_system.add(MemoryType.SHORT_TERM, memory_entry)
    retrieved_memory = await memory_system.retrieve(MemoryType.SHORT_TERM, memory_id)
    assert retrieved_memory.content == "Test memory content"
    assert retrieved_memory.metadata == {"key": "value"}

@pytest.mark.asyncio
async def test_search_memory(memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now())
    )
    await memory_system.add(MemoryType.SHORT_TERM, memory_entry)
    search_results = await memory_system.search(AdvancedSearchQuery(query="test", memory_type=MemoryType.SHORT_TERM))
    assert len(search_results) > 0
    assert search_results[0].content == "Test memory content"
