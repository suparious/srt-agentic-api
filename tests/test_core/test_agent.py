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
