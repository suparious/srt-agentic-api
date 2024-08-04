import os
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings
from app.api.models.agent import AgentConfig, MemoryConfig
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

@pytest.fixture(scope="module")
def test_app(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

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
async def test_agent(async_client, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": AgentConfig(
            llm_provider="vllm",
            model_name="mistral-7b-instruct-v0.1",
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
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()["agent_id"]
