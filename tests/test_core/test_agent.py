import pytest
from unittest.mock import Mock, patch
from uuid import UUID
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig


@pytest.fixture
def mock_llm_provider():
    return Mock()


@pytest.fixture
def mock_memory_system():
    return Mock()


@pytest.fixture
def agent_config():
    return AgentConfig(
        llm_provider="test_provider",
        model_name="test_model",
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        )
    )

@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
@pytest.mark.asyncio
async def test_agent_initialization(mock_llm_provider, mock_memory_system, agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    with patch('app.core.agent.create_llm_provider', return_value=mock_llm_provider):
        agent = Agent(
            agent_id=agent_id,
            name="Test Agent",
            config=agent_config,
            memory_config=agent_config.memory_config
        )

    assert agent.id == agent_id
    assert agent.name == "Test Agent"
    assert agent.config == agent_config
    assert agent.llm_provider == mock_llm_provider

@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
@pytest.mark.asyncio
async def test_agent_process_message(mock_memory_system, mock_create_llm_provider, agent_config):
    mock_llm_provider = Mock()
    mock_create_llm_provider.return_value = mock_llm_provider
    mock_llm_provider.generate.return_value = "Processed message response"

    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    message = "Test message"
    response, function_calls = await agent.process_message(message)

    assert response == "Processed message response"
    assert function_calls == []
    mock_llm_provider.generate.assert_called_once()
    agent.memory.add.assert_called_once()


@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
def test_agent_execute_function(mock_memory_system, mock_create_llm_provider, agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    def test_function(param1, param2):
        return f"Executed with {param1} and {param2}"

    agent.available_function_ids = ["test_function_id"]
    with patch.dict('app.core.agent.registered_functions', {"test_function_id": Mock(implementation=test_function)}):
        result = agent.execute_function("test_function", {"param1": "value1", "param2": "value2"})

    assert result == "Executed with value1 and value2"


def test_agent_get_available_functions(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    agent.available_function_ids = ["function1", "function2"]
    with patch.dict('app.core.agent.registered_functions', {
        "function1": Mock(name="Function 1"),
        "function2": Mock(name="Function 2")
    }):
        available_functions = agent.get_available_functions()

    assert len(available_functions) == 2
    assert available_functions[0].name == "Function 1"
    assert available_functions[1].name == "Function 2"