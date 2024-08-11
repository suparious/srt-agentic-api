import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock
from app.core.memory.vector_memory import VectorMemory
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType

@pytest.fixture
def mock_chroma_client(mock_factory):
    mock_client = mock_factory.create_async_mock(object)  # Replace 'object' with the actual Chroma client class if available
    mock_collection = mock_factory.create_async_mock(object)  # Replace 'object' with the actual Chroma collection class if available
    mock_client.get_or_create_collection.return_value = mock_collection
    return mock_client

@pytest.fixture
def vector_memory(mock_chroma_client):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    vector_memory = VectorMemory(f"agent_{agent_id}")
    vector_memory.client = mock_chroma_client
    vector_memory.collection = mock_chroma_client.get_or_create_collection.return_value
    return vector_memory

@pytest.mark.asyncio
async def test_add_memory(vector_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    await vector_memory.add(memory_entry)
    vector_memory.collection.add.assert_called_once()
    call_args = vector_memory.collection.add.call_args[1]
    assert len(call_args['documents']) == 1
    assert call_args['documents'][0] == memory_entry.content
    assert 'key' in call_args['metadatas'][0]
    assert call_args['metadatas'][0]['key'] == 'value'

@pytest.mark.asyncio
async def test_advanced_search(vector_memory):
    query = AdvancedSearchQuery(
        query="test query",
        memory_type=MemoryType.LONG_TERM,
        context_type="test_context",
        time_range={
            "start": datetime.now() - timedelta(days=1),
            "end": datetime.now()
        },
        metadata_filters={"key": "value"},
        relevance_threshold=0.5,
        max_results=5
    )

    mock_results = {
        'ids': [['1', '2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[
            {'context_type': 'test_context', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'},
            {'context_type': 'test_context', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'}
        ]],
        'distances': [[0.1, 0.6]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 1  # Only one result should pass the relevance threshold
    assert results[0]['id'] == '1'
    assert isinstance(results[0]['memory_entry'], MemoryEntry)
    assert results[0]['relevance_score'] >= 0.5

    # Verify that the query was constructed correctly
    vector_memory.collection.query.assert_called_once()
    call_args = vector_memory.collection.query.call_args[1]
    assert call_args['query_texts'] == ["test query"]
    assert call_args['n_results'] == 5
    assert call_args['where']['context_type'] == "test_context"
    assert call_args['where']['context_timestamp']['$gte'] == query.time_range['start'].isoformat()
    assert call_args['where']['context_timestamp']['$lte'] == query.time_range['end'].isoformat()
    assert call_args['where']['key'] == "value"

@pytest.mark.asyncio
async def test_advanced_search_with_query(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = {
        'ids': [['1', '2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat(), 'key': 'value1'},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat(), 'key': 'value2'}
        ]],
        'distances': [[0.1, 0.2]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2
    assert results[0]['id'] == '1'
    assert results[1]['id'] == '2'
    assert isinstance(results[0]['memory_entry'], MemoryEntry)
    assert isinstance(results[1]['memory_entry'], MemoryEntry)


@pytest.mark.asyncio
async def test_advanced_search_with_filters(vector_memory):
    query = AdvancedSearchQuery(
        query="test query",
        context_type="test_type",
        time_range={"start": datetime.now() - timedelta(days=1), "end": datetime.now()},
        metadata_filters={"key": "value"},
        max_results=5
    )
    mock_results = {
        'ids': [['1']],
        'documents': [['doc1']],
        'metadatas': [[{'context_type': 'test_type', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'}]],
        'distances': [[0.1]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 1
    assert results[0]['memory_entry'].context.context_type == "test_type"
    assert results[0]['memory_entry'].metadata["key"] == "value"


@pytest.mark.asyncio
async def test_advanced_search_with_relevance_threshold(vector_memory):
    query = AdvancedSearchQuery(query="test query", relevance_threshold=0.5, max_results=5)
    mock_results = {
        'ids': [['1', '2', '3']],
        'documents': [['doc1', 'doc2', 'doc3']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()}
        ]],
        'distances': [[0.1, 0.5, 0.9]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2  # Only two results should have relevance score >= 0.5
    assert all(result['relevance_score'] >= 0.5 for result in results)


@pytest.mark.asyncio
async def test_advanced_search_empty_results(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 0


@pytest.mark.asyncio
async def test_advanced_search_with_max_results(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=2)
    mock_results = {
        'ids': [['1', '2', '3']],
        'documents': [['doc1', 'doc2', 'doc3']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()}
        ]],
        'distances': [[0.1, 0.2, 0.3]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2  # Only two results should be returned due to max_results
    assert results[0]['id'] == '1'
    assert results[1]['id'] == '2'
