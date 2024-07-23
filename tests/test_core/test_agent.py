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
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        assert agent.id == agent_id
        assert agent.name == agent_name
        assert agent.config == agent_config
        assert isinstance(agent.llm_provider, AsyncMock)
        assert isinstance(agent.memory, AsyncMock)


@pytest.mark.asyncio
async def test_agent_process_message(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"
    test_message = "Hello, Agent!"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_llm_provider.generate.return_value = "Generated response"
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        mock_memory_system.retrieve_relevant.return_value = []
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        response, function_calls = await agent.process_message(test_message)

        assert response == "Generated response"
        assert function_calls == []
        mock_memory_system.retrieve_relevant.assert_called_once_with(test_message)
        mock_llm_provider.generate.assert_called_once()
        mock_memory_system.add.assert_called_once()


@pytest.mark.asyncio
async def test_agent_execute_function(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        async def test_function(param1, param2):
            return f"Executed with {param1} and {param2}"

        mock_function = AsyncMock(side_effect=test_function)
        mock_function.id = "test_function_id"
        agent.get_function_by_name = Mock(return_value=mock_function)

        with patch.dict('app.core.agent.registered_functions', {"test_function_id": mock_function}):
            result = await agent.execute_function(
                function_name="test_function",
                parameters={"param1": "value1", "param2": "value2"}
            )

        assert result == "Executed with value1 and value2"
        agent.get_function_by_name.assert_called_once_with("test_function")
        mock_function.assert_awaited_once_with(param1="value1", param2="value2")


@pytest.mark.asyncio
async def test_agent_get_available_functions(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider'), patch('app.core.agent.MemorySystem'):
        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        mock_function1 = Mock(id="func1", name="Function 1")
        mock_function2 = Mock(id="func2", name="Function 2")

        with patch.dict('app.core.agent.registered_functions', {
            "func1": mock_function1,
            "func2": mock_function2
        }):
            agent.available_function_ids = ["func1", "func2"]
            available_functions = agent.get_available_functions()

        assert len(available_functions) == 2
        assert available_functions[0].name == "Function 1"
        assert available_functions[1].name == "Function 2"
