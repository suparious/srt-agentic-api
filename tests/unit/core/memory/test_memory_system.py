import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.core.memory.memory_system import MemorySystem
from app.api.models.agent import MemoryConfig
from app.api.models.memory import MemoryType, MemoryEntry, AdvancedSearchQuery, MemoryOperation, MemoryContext

@pytest.fixture
def mock_redis_memory():
    mock = AsyncMock()
    mock.add.return_value = "mock_memory_id"
    return mock

@pytest.fixture
def mock_vector_memory():
    return AsyncMock()

@pytest.fixture
def memory_config():
    return MemoryConfig(use_long_term_memory=True, use_redis_cache=True)

@pytest.fixture
def memory_system(mock_redis_memory, mock_vector_memory, memory_config):
    return MemorySystem(
        agent_id=UUID('12345678-1234-5678-1234-567812345678'),
        config=memory_config,
        short_term=mock_redis_memory,
        long_term=mock_vector_memory
    )

@pytest.mark.asyncio
async def test_add_short_term_memory(memory_system, mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    result = await memory_system.add(MemoryType.SHORT_TERM, memory_entry)

    assert result == "mock_memory_id"
    mock_redis_memory.add.assert_called_once_with(memory_entry)

@pytest.mark.asyncio
async def test_add_long_term_memory(memory_system, mock_vector_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_vector_memory.add.return_value = "memory_id_2"

    result = await memory_system.add(MemoryType.LONG_TERM, memory_entry)

    assert result == "memory_id_2"
    mock_vector_memory.add.assert_called_once_with(memory_entry)

@pytest.mark.asyncio
async def test_retrieve_short_term_memory(memory_system, mock_redis_memory):
    mock_memory = MemoryEntry(
        content="Retrieved content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_redis_memory.get.return_value = mock_memory

    result = await memory_system.retrieve(MemoryType.SHORT_TERM, "memory_id_1")

    assert result == mock_memory
    mock_redis_memory.get.assert_called_once_with("memory_id_1")

@pytest.mark.asyncio
async def test_retrieve_long_term_memory(memory_system, mock_vector_memory):
    mock_memory = MemoryEntry(
        content="Retrieved content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_vector_memory.get.return_value = mock_memory

    result = await memory_system.retrieve(MemoryType.LONG_TERM, "memory_id_2")

    assert result == mock_memory
    mock_vector_memory.get.assert_called_once_with("memory_id_2")

@pytest.mark.asyncio
async def test_search(memory_system, mock_redis_memory, mock_vector_memory):
    query = AdvancedSearchQuery(query="test", max_results=5)
    mock_redis_memory.search.return_value = [{"id": "1", "relevance_score": 0.9}]
    mock_vector_memory.search.return_value = [{"id": "2", "relevance_score": 0.8}]

    results = await memory_system.search(query)

    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"
    mock_redis_memory.search.assert_called_once_with(query)
    mock_vector_memory.search.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_delete_short_term_memory(memory_system, mock_redis_memory):
    await memory_system.delete(MemoryType.SHORT_TERM, "memory_id_1")

    mock_redis_memory.delete.assert_called_once_with("memory_id_1")

@pytest.mark.asyncio
async def test_delete_long_term_memory(memory_system, mock_vector_memory):
    await memory_system.delete(MemoryType.LONG_TERM, "memory_id_2")

    mock_vector_memory.delete.assert_called_once_with("memory_id_2")

@pytest.mark.asyncio
async def test_perform_operation_add(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    result = await memory_system.perform_operation(MemoryOperation.ADD, MemoryType.SHORT_TERM, memory_entry.model_dump())
    assert isinstance(result, str)
    assert result == "mock_memory_id"

@pytest.mark.asyncio
async def test_retrieve_relevant(memory_system, mock_redis_memory, mock_vector_memory):
    mock_redis_memory.get_recent.return_value = [{"id": "1", "timestamp": datetime.now()}]
    mock_vector_memory.search.return_value = [{"id": "2", "timestamp": datetime.now()}]

    results = await memory_system.retrieve_relevant("test context")

    assert len(results) == 2
    mock_redis_memory.get_recent.assert_called_once()
    mock_vector_memory.search.assert_called_once()

@pytest.mark.asyncio
async def test_consolidate_memories(memory_system, mock_redis_memory, mock_vector_memory):
    old_memories = [
        MemoryEntry(
            content="Old content",
            metadata={"key": "value"},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(hours=2), metadata={})
        )
    ]
    mock_redis_memory.get_memories_older_than.return_value = old_memories

    await memory_system.consolidate_memories()

    mock_redis_memory.get_memories_older_than.assert_called_once()
    mock_vector_memory.add.assert_called_once_with(old_memories[0])
    mock_redis_memory.delete.assert_called_once()

@pytest.mark.asyncio
async def test_forget_old_memories(memory_system, mock_vector_memory):
    old_memories = [
        MemoryEntry(
            content="Very old content",
            metadata={"key": "value"},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(days=30), metadata={})
        )
    ]
    mock_vector_memory.get_memories_older_than.return_value = old_memories

    await memory_system.forget_old_memories(timedelta(days=30))

    mock_vector_memory.get_memories_older_than.assert_called_once()
    mock_vector_memory.delete.assert_called_once()

@pytest.mark.asyncio
async def test_close(memory_system, mock_redis_memory, mock_vector_memory):
    await memory_system.close()

    mock_redis_memory.close.assert_called_once()
    mock_vector_memory.close.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_memory_type(memory_system):
    with pytest.raises(ValueError):
        await memory_system.add("INVALID_TYPE", MagicMock())

@pytest.mark.asyncio
async def test_invalid_operation(memory_system):
    with pytest.raises(ValueError):
        await memory_system.perform_operation("INVALID_OPERATION", MemoryType.SHORT_TERM, {})
