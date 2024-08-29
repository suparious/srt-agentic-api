import pytest
from uuid import UUID
from unittest.mock import AsyncMock, MagicMock
from app.core.agent import Agent
from app.core.models import AgentConfig, MemoryConfig
from app.core.function_manager import FunctionManager
from app.core.memory import MemorySystem

@pytest.fixture
def mock_factory():
    class MockFactory:
        def create_mock(self, cls):
            return MagicMock(spec=cls)
    return MockFactory()

@pytest.fixture
def test_agent_id():
    return UUID('12345678-1234-5678-1234-567812345678')

@pytest.fixture
def test_agent_config():
    return AgentConfig(
        llm_providers=[{"provider_type": "mock", "model_name": "mock-model"}],
        temperature=0.7,
        max_tokens=150,
        memory_config=MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
    )

@pytest.fixture
async def test_agent(test_agent_id, test_agent_config, mock_factory, mock_llm_provider):
    mock_function_manager = mock_factory.create_mock(FunctionManager)
    mock_memory_system = mock_factory.create_mock(MemorySystem)
    agent = Agent(
        agent_id=test_agent_id,
        name="Test Agent",
        config=test_agent_config,
        function_manager=mock_function_manager,
        llm_provider=mock_llm_provider,
        memory=mock_memory_system
    )
    await agent.initialize()
    yield agent
    await agent.cleanup()

@pytest.fixture
def mock_agent():
    return AsyncMock(spec=Agent)

@pytest.fixture(autouse=True)
async def agent_isolation(request, test_agent):
    if "agent" in request.keywords:
        # Perform any necessary setup for agent isolation
        yield
        # Perform any necessary cleanup for agent isolation
    else:
        yield
