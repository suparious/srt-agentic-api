import json
import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig, LLMProviderConfig
from app.api.models.memory import MemoryType, MemoryEntry, MemoryContext, MemoryOperation
from app.core.llm_provider import LLMProvider
from app.core.function_manager import FunctionManager
from app.core.memory import MemorySystem
from app.config import LLMProviderConfig

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_llm_provider():
    return AsyncMock(spec=LLMProvider)

@pytest.fixture
def test_agent_config():
    return AgentConfig(
        llm_providers=[LLMProviderConfig(
            provider_type="mock",
            model_name="mock-model"
        )],
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
    )

@pytest.fixture
def mock_function_manager():
    return MagicMock(spec=FunctionManager)

@pytest.fixture
def mock_memory_system():
    return AsyncMock(spec=MemorySystem)

@pytest.fixture
def test_agent(test_agent_config, mock_function_manager, mock_memory_system, mock_llm_provider):
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.core.agent.create_llm_provider", lambda: mock_llm_provider)
        agent = Agent(UUID('12345678-1234-5678-1234-567812345678'), "Test Agent", test_agent_config, mock_function_manager)
        agent.memory = mock_memory_system
        return agent

async def test_advanced_search(test_agent, mock_memory_system):
    # Mock memory system's advanced search method
    mock_memory_system.search.return_value = [
        {"content": "Test memory content 1", "metadata": {"key": "value"}, "relevance_score": 0.8},
        {"content": "Test memory content 2", "metadata": {"key": "value"}, "relevance_score": 0.6}
    ]

    search_params = {
        "query": "Test memory",
        "memory_type": MemoryType.LONG_TERM,
        "context_type": "test_context",
        "time_range": {
            "start": datetime.now() - timedelta(hours=3),
            "end": datetime.now()
        },
        "metadata_filters": {"key": "value"},
        "relevance_threshold": 0.5,
        "max_results": 2
    }

    results = await test_agent.memory.search(search_params)

    assert len(results) == 2
    for result in results:
        assert "Test memory" in result["content"]
        assert result["metadata"]["key"] == "value"
        assert result["relevance_score"] >= 0.5

    mock_memory_system.search.assert_called_once()

async def test_add_memory(test_agent, mock_memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test_context",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    mock_memory_system.add.return_value = "test_memory_id"

    memory_id = await test_agent.memory.add(MemoryType.SHORT_TERM, memory_entry)

    assert memory_id == "test_memory_id"
    mock_memory_system.add.assert_called_once_with(MemoryType.SHORT_TERM, memory_entry)

async def test_retrieve_memory(test_agent, mock_memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test_context",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    mock_memory_system.retrieve.return_value = memory_entry

    retrieved_memory = await test_agent.memory.retrieve(MemoryType.SHORT_TERM, "test_memory_id")

    assert retrieved_memory == memory_entry
    mock_memory_system.retrieve.assert_called_once_with(MemoryType.SHORT_TERM, "test_memory_id")

async def test_search_memory(test_agent, mock_memory_system):
    mock_memory_system.search.return_value = [
        {"content": "Test memory content", "metadata": {"key": "value"}, "relevance_score": 0.8}
    ]

    search_results = await test_agent.memory.search({
        "query": "Test memory",
        "memory_type": MemoryType.SHORT_TERM,
        "max_results": 5
    })

    assert len(search_results) == 1
    assert search_results[0]["content"] == "Test memory content"
    assert "relevance_score" in search_results[0]
    mock_memory_system.search.assert_called_once()

async def test_delete_memory(test_agent, mock_memory_system):
    await test_agent.memory.delete(MemoryType.SHORT_TERM, "test_memory_id")
    mock_memory_system.delete.assert_called_once_with(MemoryType.SHORT_TERM, "test_memory_id")

async def test_memory_operation(test_agent, mock_memory_system):
    operation_data = {
        "content": "Test operation memory content",
        "metadata": {"operation": "test"},
        "context": {
            "context_type": "test_operation",
            "timestamp": datetime.now(),
            "metadata": {}
        }
    }

    mock_memory_system.perform_operation.return_value = "Operation result"

    result = await test_agent.memory.perform_operation(MemoryOperation.ADD, MemoryType.SHORT_TERM, operation_data)

    assert result == "Operation result"
    mock_memory_system.perform_operation.assert_called_once_with(MemoryOperation.ADD, MemoryType.SHORT_TERM, operation_data)

@pytest.mark.asyncio
async def test_process_message(test_agent, mock_llm_provider):
    mock_llm_provider.generate.return_value = "Test response"
    test_agent.memory.retrieve_relevant.return_value = []

    response, function_calls = await test_agent.process_message("Test message")

    assert response == "Test response"
    assert isinstance(function_calls, list)
    mock_llm_provider.generate.assert_called_once()
    test_agent.memory.add.assert_called_once()

async def test_execute_function(test_agent, mock_function_manager):
    mock_function = AsyncMock()
    mock_function.implementation.return_value = "Function result"
    mock_function_manager.registered_functions = {"func1": mock_function}
    test_agent.available_function_ids = ["func1"]

    result = await test_agent.execute_function("func1", {"param": "value"})

    assert result == "Function result"
    mock_function.implementation.assert_called_once_with(param="value")

def test_get_available_functions(test_agent, mock_function_manager):
    mock_function_manager.registered_functions = {
        "func1": MagicMock(name="Function1"),
        "func2": MagicMock(name="Function2")
    }
    test_agent.available_function_ids = ["func1", "func2"]

    available_functions = test_agent.get_available_functions()

    assert len(available_functions) == 2
    assert available_functions[0].name == "Function1"
    assert available_functions[1].name == "Function2"

def test_add_function(test_agent, mock_function_manager):
    mock_function_manager.registered_functions = {"func1": MagicMock(name="Function1")}

    test_agent.add_function("func1")

    assert "func1" in test_agent.available_function_ids

def test_remove_function(test_agent):
    test_agent.available_function_ids = ["func1", "func2"]

    test_agent.remove_function("func1")

    assert "func1" not in test_agent.available_function_ids
    assert "func2" in test_agent.available_function_ids

def test_get_function_by_name(test_agent, mock_function_manager):
    mock_function = MagicMock(name="Function1")
    mock_function_manager.registered_functions = {"func1": mock_function}
    test_agent.available_function_ids = ["func1"]

    result = test_agent.get_function_by_name("Function1")

    assert result == mock_function

def test_prepare_prompt(test_agent):
    context = [{"content": "Context 1"}, {"content": "Context 2"}]
    test_agent.conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]

    prompt = test_agent._prepare_prompt(context)

    assert "Context: Context 1" in prompt
    assert "Context: Context 2" in prompt
    assert "user: Hello" in prompt
    assert "assistant: Hi there" in prompt

def test_parse_response(test_agent):
    response = "This is a response. FUNCTION CALL: test_function(param1='value1', param2=42)"

    response_text, function_calls = test_agent._parse_response(response)

    assert response_text == "This is a response."
    assert len(function_calls) == 1
    assert function_calls[0]["name"] == "test_function"
    assert function_calls[0]["arguments"] == {"param1": "value1", "param2": 42}
