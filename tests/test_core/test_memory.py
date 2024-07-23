import pytest
from uuid import UUID
from unittest.mock import AsyncMock, patch
from app.core.memory import RedisMemory, VectorMemory, MemorySystem
from app.api.models.memory import MemoryType, MemoryEntry
from app.api.models.agent import MemoryConfig

@pytest.fixture
def memory_config():
    return MemoryConfig(use_long_term_memory=True, use_redis_cache=True)

@pytest.mark.asyncio
async def test_redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')

    with patch('app.core.memory.redis_memory.aioredis') as mock_redis:
        mock_redis_client = AsyncMock()
        mock_redis.from_url.return_value = mock_redis_client

        redis_memory = RedisMemory("redis://localhost:6379", agent_id)

        # Test add
        await redis_memory.add("test_key", "test_value")
        mock_redis_client.set.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key", "test_value", ex=3600)

        # Test get
        mock_redis_client.get.return_value = "test_value"
        value = await redis_memory.get("test_key")
        assert value == "test_value"
        mock_redis_client.get.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key")

        # Test delete
        await redis_memory.delete("test_key")
        mock_redis_client.delete.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key")

@pytest.mark.asyncio
async def test_vector_memory():
    with patch('app.core.memory.vector_memory.chromadb') as mock_chromadb:
        mock_client = AsyncMock()
        mock_collection = AsyncMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        vector_memory = VectorMemory("test_collection", mock_chromadb.config.Settings())

        # Test add
        await vector_memory.add("test_id", "test_content", {"key": "value"})
        mock_collection.add.assert_called_once_with(documents=["test_content"], metadatas=[{"key": "value"}], ids=["test_id"])

        # Test search
        mock_collection.query.return_value = {
            "ids": [["test_id"]],
            "documents": [["test_content"]],
            "metadatas": [[{"key": "value"}]]
        }
        results = await vector_memory.search("test query")
        assert results == [{"id": "test_id", "content": "test_content", "metadata": {"key": "value"}}]
        mock_collection.query.assert_called_once_with(query_texts=["test query"], n_results=5)

@pytest.mark.asyncio
async def test_memory_system(memory_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')

    with patch('app.core.memory.memory_system.RedisMemory') as MockRedisMemory, \
            patch('app.core.memory.memory_system.VectorMemory') as MockVectorMemory:
        mock_redis = AsyncMock()
        mock_vector = AsyncMock()
        MockRedisMemory.return_value = mock_redis
        MockVectorMemory.return_value = mock_vector

        memory_system = MemorySystem(agent_id, memory_config)

        # Test add (short-term memory)
        await memory_system.add(MemoryType.SHORT_TERM, "test_content", {"key": "value"})
        mock_redis.add.assert_called_once()

        # Test add (long-term memory)
        await memory_system.add(MemoryType.LONG_TERM, "test_content", {"key": "value"})
        mock_vector.add.assert_called_once()

        # Test retrieve (short-term memory)
        mock_redis.get.return_value = "test_content"
        result = await memory_system.retrieve(MemoryType.SHORT_TERM, "test_id")
        assert result == MemoryEntry(content="test_content")

        # Test retrieve (long-term memory)
        mock_vector.search.return_value = [{"id": "test_id", "content": "test_content", "metadata": {"key": "value"}}]
        result = await memory_system.retrieve(MemoryType.LONG_TERM, "test_id")
        assert result == MemoryEntry(content="test_content", metadata={"key": "value"})

        # Test search
        results = await memory_system.search(MemoryType.LONG_TERM, "test query")
        assert results == [MemoryEntry(content="test_content", metadata={"key": "value"})]

        # Test delete
        await memory_system.delete(MemoryType.SHORT_TERM, "test_id")
        mock_redis.delete.assert_called_once()

@pytest.mark.asyncio
async def test_memory_system_integration(memory_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    memory_system = MemorySystem(agent_id, memory_config)

    # Test add and retrieve (short-term memory)
    short_term_id = await memory_system.add(MemoryType.SHORT_TERM, "short-term content")
    short_term_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert short_term_result.content == "short-term content"

    # Test add and retrieve (long-term memory)
    long_term_id = await memory_system.add(MemoryType.LONG_TERM, "long-term content", {"type": "test"})
    long_term_result = await memory_system.retrieve(MemoryType.LONG_TERM, long_term_id)
    assert long_term_result.content == "long-term content"
    assert long_term_result.metadata == {"type": "test"}

    # Test search
    search_results = await memory_system.search(MemoryType.LONG_TERM, "long-term")
    assert len(search_results) > 0
    assert search_results[0].content == "long-term content"

    # Test delete
    await memory_system.delete(MemoryType.SHORT_TERM, short_term_id)
    deleted_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert deleted_result is None
