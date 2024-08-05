import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from app.core.memory import RedisMemory, VectorMemory, MemorySystem
from app.api.models.memory import MemoryType, MemoryEntry, MemoryContext, AdvancedSearchQuery
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

        redis_memory = RedisMemory(agent_id)

        # Test add
        memory_entry = MemoryEntry(
            content="test_content",
            metadata={"key": "value"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now(),
                metadata={}
            )
        )
        await redis_memory.add("test_key", memory_entry)
        mock_redis_client.set.assert_called_once()

        # Test get
        mock_redis_client.get.return_value = memory_entry.model_dump_json()
        retrieved_entry = await redis_memory.get("test_key")
        assert retrieved_entry == memory_entry
        mock_redis_client.get.assert_called_once()

        # Test delete
        await redis_memory.delete("test_key")
        mock_redis_client.delete.assert_called_once()

        # Test advanced search
        mock_redis_client.scan.return_value = (0, ["test_key"])
        mock_redis_client.get.return_value = memory_entry.model_dump_json()
        query = AdvancedSearchQuery(
            query="test",
            memory_type=MemoryType.SHORT_TERM,
            context_type="test_context",
            time_range={"start": datetime.now() - timedelta(hours=1), "end": datetime.now()},
            metadata_filters={"key": "value"},
            relevance_threshold=0.5,
            max_results=10
        )
        results = await redis_memory.search(query)
        assert len(results) == 1
        assert results[0]["memory_entry"] == memory_entry
        assert "relevance_score" in results[0]

@pytest.mark.asyncio
async def test_vector_memory():
    with patch('app.core.memory.vector_memory.PersistentClient') as mock_chroma:
        mock_client = AsyncMock()
        mock_collection = AsyncMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chroma.return_value = mock_client

        vector_memory = VectorMemory("test_collection")

        # Test add
        memory_entry = MemoryEntry(
            content="test_content",
            metadata={"key": "value"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now(),
                metadata={}
            )
        )
        await vector_memory.add("test_id", memory_entry)
        mock_collection.add.assert_called_once()

        # Test search
        mock_collection.query.return_value = {
            "ids": [["test_id"]],
            "documents": [["test_content"]],
            "metadatas": [[{"key": "value", "context_type": "test_context", "context_timestamp": datetime.now().isoformat()}]],
            "distances": [[0.1]]
        }
        query = AdvancedSearchQuery(
            query="test",
            memory_type=MemoryType.LONG_TERM,
            context_type="test_context",
            time_range={"start": datetime.now() - timedelta(hours=1), "end": datetime.now()},
            metadata_filters={"key": "value"},
            relevance_threshold=0.5,
            max_results=10
        )
        results = await vector_memory.search(query)
        assert len(results) == 1
        assert results[0]["memory_entry"].content == "test_content"
        assert "relevance_score" in results[0]
        mock_collection.query.assert_called_once()

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
        memory_entry = MemoryEntry(
            content="short_term_content",
            metadata={"key": "value"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now(),
                metadata={}
            )
        )
        await memory_system.add(MemoryType.SHORT_TERM, memory_entry)
        mock_redis.add.assert_called_once()

        # Test add (long-term memory)
        memory_entry = MemoryEntry(
            content="long_term_content",
            metadata={"key": "value"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now(),
                metadata={}
            )
        )
        await memory_system.add(MemoryType.LONG_TERM, memory_entry)
        mock_vector.add.assert_called_once()

        # Test retrieve (short-term memory)
        mock_redis.get.return_value = MemoryEntry(
            content="short_term_content",
            metadata={"key": "value"},
            context=MemoryContext(
                context_type="test_context",
                timestamp=datetime.now(),
                metadata={}
            )
        )
        result = await memory_system.retrieve(MemoryType.SHORT_TERM, "test_id")
        assert result.content == "short_term_content"

        # Test advanced search
        mock_redis.search.return_value = [
            {"id": "test_id", "memory_entry": memory_entry, "relevance_score": 0.9}
        ]
        mock_vector.search.return_value = [
            {"id": "test_id", "memory_entry": memory_entry, "relevance_score": 0.8}
        ]
        query = AdvancedSearchQuery(
            query="test",
            memory_type=None,  # Search both short-term and long-term
            context_type="test_context",
            time_range={"start": datetime.now() - timedelta(hours=1), "end": datetime.now()},
            metadata_filters={"key": "value"},
            relevance_threshold=0.5,
            max_results=10
        )
        results = await memory_system.search(query)
        assert len(results) == 2
        assert all("relevance_score" in result for result in results)
        mock_redis.search.assert_called_once()
        mock_vector.search.assert_called_once()

@pytest.mark.asyncio
async def test_memory_system_integration(memory_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    memory_system = MemorySystem(agent_id, memory_config)

    # Test add and retrieve (short-term memory)
    short_term_entry = MemoryEntry(
        content="short-term content",
        metadata={"type": "short"},
        context=MemoryContext(
            context_type="test",
            timestamp=datetime.now(),
            metadata={}
        )
    )
    short_term_id = await memory_system.add(MemoryType.SHORT_TERM, short_term_entry)
    short_term_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert short_term_result == short_term_entry

    # Test add and retrieve (long-term memory)
    long_term_entry = MemoryEntry(
        content="long-term content",
        metadata={"type": "long"},
        context=MemoryContext(
            context_type="test",
            timestamp=datetime.now(),
            metadata={}
        )
    )
    long_term_id = await memory_system.add(MemoryType.LONG_TERM, long_term_entry)
    long_term_result = await memory_system.retrieve(MemoryType.LONG_TERM, long_term_id)
    assert long_term_result == long_term_entry

    # Test advanced search
    query = AdvancedSearchQuery(
        query="content",
        memory_type=None,  # Search both short-term and long-term
        context_type="test",
        time_range={"start": datetime.now() - timedelta(hours=1), "end": datetime.now()},
        metadata_filters=None,
        relevance_threshold=0.5,
        max_results=10
    )
    search_results = await memory_system.search(query)
    assert len(search_results) == 2
    assert all("relevance_score" in result for result in search_results)
    assert any(result["memory_entry"].content == "short-term content" for result in search_results)
    assert any(result["memory_entry"].content == "long-term content" for result in search_results)

    # Test delete
    await memory_system.delete(MemoryType.SHORT_TERM, short_term_id)
    deleted_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert deleted_result is None
