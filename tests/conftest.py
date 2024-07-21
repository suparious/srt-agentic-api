import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings
from app.core.agent import create_agent
from app.api.models.agent import AgentConfig, MemoryConfig

@pytest.fixture
def test_settings():
    return Settings(
        API_KEY="test_api_key",
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],
        REDIS_URL="redis://localhost:6379/1",
        CHROMA_PERSIST_DIRECTORY="./test_chroma_db",
        OPENAI_API_KEY="test_openai_key",
        ANTHROPIC_API_KEY="test_anthropic_key",
        VLLM_API_BASE="http://test-vllm-api-endpoint",
        LLAMACPP_API_BASE="http://test-llamacpp-server-endpoint",
        TGI_API_BASE="http://test-tgi-server-endpoint",
    )

@pytest.fixture
def app_with_test_settings(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(app_with_test_settings):
    async with AsyncClient(app=app_with_test_settings, base_url="http://test") as client:
        yield client

@pytest.fixture
def sync_client(app_with_test_settings):
    return TestClient(app_with_test_settings)

@pytest.fixture
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}

@pytest.fixture
async def test_agent(async_client, auth_headers):
    agent_data = {
        "name": "Test Agent",
        "config": AgentConfig(
            llm_provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ),
        "initial_prompt": "You are a helpful assistant."
    }
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()["agent_id"]
