import os
import pytest
import asyncio
from httpx import AsyncClient
from uuid import UUID
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app
from app.config import Settings
from app.api.models.agent import AgentConfig, MemoryConfig, LLMProviderConfig
from app.core.llm_provider import LLMProvider
from app.core.memory.redis_memory import RedisMemory
from dotenv import load_dotenv

# Set the TESTING environment variable
os.environ["TESTING"] = "true"

# Load the test environment variables
load_dotenv('.env.test')

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        API_KEY=os.getenv('API_KEY', 'your_api_key_here'),
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],
        REDIS_URL="redis://localhost:6379/15",
        CHROMA_PERSIST_DIRECTORY="./test_chroma_db",
        OPENAI_API_KEY="test_openai_key",
        VLLM_API_BASE="https://artemis.hq.solidrust.net/v1",
        LLAMACPP_API_BASE="http://test-llamacpp-server-endpoint",
        TGI_API_BASE="http://test-tgi-server-endpoint",
        ANTHROPIC_API_KEY="test_anthropic_key",
        TESTING=True
    )

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def test_app(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def redis_memory(event_loop):
    redis_mem = RedisMemory(UUID('00000000-0000-0000-0000-000000000000'))
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()
    await RedisMemory.close_pool()

@pytest.fixture
async def async_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

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
async def test_agent(async_client, auth_headers, redis_memory, mock_llm_provider):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": AgentConfig(
            llm_providers=[
                LLMProviderConfig(
                    provider_type="mock",
                    model_name="mock-model"
                )
            ],
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ).model_dump(),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ).model_dump(),
        "initial_prompt": "You are a helpful assistant."
    }

    # Mock the LLM provider creation
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.core.agent.create_llm_provider", lambda _: mock_llm_provider)
        response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)

    assert response.status_code == 201
    return response.json()["agent_id"]

# Add a fixture to clean up Redis after each test
@pytest.fixture(autouse=True)
async def cleanup_redis(redis_memory):
    yield
    async with redis_memory.get_connection() as conn:
        await conn.flushdb()

@pytest.fixture(autouse=True, scope="session")
async def cleanup_after_tests(redis_memory):
    yield
    await redis_memory.close()
    await RedisMemory.close_pool()
