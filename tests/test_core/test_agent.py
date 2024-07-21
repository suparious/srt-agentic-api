import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig


@pytest.fixture
def agent_config():
    return AgentConfig(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        )
    )


@pytest.mark.asyncio
async def test_agent_initialization(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        agent = Agent(
            agent_id=agent_id,
            name="Test Agent",
            config=agent_config,
            memory_config=agent_config.memory_config
        )

        assert agent.id == agent_id
        assert agent.name == "Test Agent"
        assert agent.config == agent_config
        assert isinstance(agent.llm_provider, Mock)
        assert isinstance(agent.memory, MockMemorySystem.return_value)


@pytest.mark.asyncio
async def test_agent_process_message(agent_config):
    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_create_llm_provider.return_value = mock_llm_provider
        mock_llm_provider.generate.return_value = "Processed message response"

        mock_memory = AsyncMock()
        MockMemorySystem.return_value = mock_memory
        mock_memory.retrieve_relevant.return_value = []

        agent_id = UUID('12345678-1234-5678-1234-567812345678')
        agent = Agent(
            agent_id=agent_id,
            name="Test Agent",
            config=agent_config,
            memory_config=agent_config.memory_config
        )

        message = "Test message"
        response, function_calls = await agent.process_message(message=message)

        assert response == "Processed message response"
        assert function_calls == []
        mock_llm_provider.generate.assert_called_once()
        mock_memory.add.assert_called_once()


@pytest.mark.asyncio
async def test_agent_execute_function(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    async def test_function(param1, param2):
        return f"Executed with {param1} and {param2}"

    mock_function = AsyncMock(implementation=test_function)
    agent.get_function_by_name = Mock(return_value=mock_function)

    result = await agent.execute_function(
        function_name="test_function",
        parameters={"param1": "value1", "param2": "value2"}
    )

    assert result == "Executed with value1 and value2"
    agent.get_function_by_name.assert_called_once_with("test_function")
    mock_function.assert_called_once_with(param1="value1", param2="value2")


def test_agent_get_available_functions(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    agent.available_function_ids = ["function1", "function2"]
    mock_function1 = Mock(name="Function 1")
    mock_function2 = Mock(name="Function 2")
    with patch.dict('app.core.agent.registered_functions', {
        "function1": mock_function1,
        "function2": mock_function2
    }):
        available_functions = agent.get_available_functions()

    assert len(available_functions) == 2
    assert available_functions[0] == mock_function1
    assert available_functions[1] == mock_function2
