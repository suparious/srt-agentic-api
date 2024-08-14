import os
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from uuid import UUID
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from dotenv import load_dotenv

from app.main import app
from app.config import Settings, LLMProviderConfig as ConfigLLMProviderConfig
from app.api.models.agent import AgentConfig, MemoryConfig, LLMProviderConfig as AgentLLMProviderConfig
from app.core.llm_provider import LLMProvider
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.redis.connection import RedisConnection
from app.core.memory.vector_memory import VectorMemory
from app.core.agent import Agent

# Set the TESTING environment variable
os.environ["TESTING"] = "true"

# Load the test environment variables
load_dotenv('.env.test')

class MockFactory:
    @staticmethod
    def create_async_mock(spec):
        mock = AsyncMock(spec=spec)
        for attr_name in dir(spec):
            if not attr_name.startswith('_'):
                attr = getattr(spec, attr_name)
                if asyncio.iscoroutinefunction(attr):
                    setattr(mock, attr_name, AsyncMock())
                elif callable(attr):
                    setattr(mock, attr_name, MagicMock())
        return mock

@pytest.fixture
def mock_factory():
    return MockFactory

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        API_KEY="your_api_key_here",
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],
        REDIS_URL="redis://localhost:6379/15",
        CHROMA_PERSIST_DIRECTORY="./test_chroma_db",
        OPENAI_API_KEY="test_openai_key",
        VLLM_API_BASE="https://artemis.hq.solidrust.net/v1",
        LLAMACPP_API_BASE="http://test-llamacpp-server-endpoint",
        TGI_API_BASE="http://test-tgi-server-endpoint",
        ANTHROPIC_API_KEY="test_anthropic_key",
        EMBEDDING_MODEL="all-MiniLM-L6-v2",
        LLM_PROVIDER_CONFIGS=[
            ConfigLLMProviderConfig(
                provider_type="vllm",
                model_name="llama-7b",
                api_base="https://artemis.hq.solidrust.net/v1"
            ),
            ConfigLLMProviderConfig(
                provider_type="openai",
                model_name="gpt-3.5-turbo",
                api_key="test_openai_key"
            ),
        ],
        TESTING=True
    )

@pytest.fixture(scope="session")
async def redis_connection(test_settings):
    connection = RedisConnection(UUID('00000000-0000-0000-0000-000000000000'))  # Use a dummy UUID for the connection
    await connection.initialize()
    yield connection
    await connection.close()

@pytest.fixture
async def redis_memory(redis_connection):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_mem = RedisMemory(agent_id)
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()

@pytest.fixture
async def mock_redis_memory():
    mock = AsyncMock(spec=RedisMemory)
    mock.initialize = AsyncMock()
    mock.close = AsyncMock()
    mock.connection = AsyncMock(spec=RedisConnection)
    mock.operations = AsyncMock()
    mock.search = AsyncMock()
    return mock

@pytest.fixture
async def mock_vector_memory():
    mock = AsyncMock(spec=VectorMemory)
    mock.collection = MagicMock()
    return mock

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
def test_app(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

@pytest.fixture(scope="module")
def sync_client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="module")
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}

@pytest.fixture
def mock_llm_provider():
    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.generate.return_value = "Mocked LLM response"
    return mock_provider

@pytest.fixture
def mock_function_manager():
    return MagicMock()

@pytest.fixture
def mock_memory_system():
    return AsyncMock()

@pytest.fixture
def test_agent_config():
    return AgentConfig(
        llm_providers=[
            AgentLLMProviderConfig(
                provider_type="mock",
                model_name="mock-model"
            )
        ],
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
    )

@pytest.fixture
async def test_agent(async_client: AsyncClient, auth_headers: dict, redis_memory, mock_llm_provider, test_agent_config):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": test_agent_config.model_dump(),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ).model_dump(),
        "initial_prompt": "You are a helpful assistant."
    }

    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.core.agent.create_llm_provider", lambda _: mock_llm_provider)
        response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)

    assert response.status_code == 201
    return response.json()["agent_id"]

@pytest.fixture
def test_agent_instance(test_agent_config, mock_function_manager, mock_memory_system):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    return Agent(agent_id, "Test Agent", test_agent_config, mock_memory_system)

@pytest.fixture(autouse=True)
async def redis_isolation(request, redis_connection):
    if "redis" in request.keywords:
        async with redis_connection.get_connection() as conn:
            await conn.flushdb()
        yield
        async with redis_connection.get_connection() as conn:
            await conn.flushdb()
    else:
        yield

@pytest.fixture(autouse=True, scope="function")
async def reset_mocks(mock_redis_memory, mock_vector_memory):
    mock_redis_memory.reset_mock()
    mock_vector_memory.reset_mock()

@pytest.fixture(autouse=True, scope="session")
async def cleanup_after_tests(event_loop):
    yield
    tasks = asyncio.all_tasks(event_loop)
    for task in tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await event_loop.shutdown_asyncgens()
