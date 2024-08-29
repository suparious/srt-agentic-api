import os
import pytest
from dotenv import load_dotenv
from unittest.mock import AsyncMock, MagicMock

# Set the TESTING environment variable
os.environ["TESTING"] = "true"

# Load the test environment variables
load_dotenv('.env.test')

class MockFactory:
    def create_async_mock(self, spec):
        return AsyncMock(spec=spec)

    def create_mock(self, spec):
        return MagicMock(spec=spec)

@pytest.fixture
def mock_factory():
    return MockFactory()

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "redis: mark test as requiring Redis"
    )

@pytest.fixture(scope="session")
def test_settings():
    from app.config import Settings
    from app.core.models.llm import LLMProviderConfig
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
            LLMProviderConfig(
                provider_type="vllm",
                model_name="llama-7b",
                api_base="https://artemis.hq.solidrust.net/v1"
            ),
            LLMProviderConfig(
                provider_type="openai",
                model_name="gpt-3.5-turbo",
                api_key="test_openai_key"
            ),
        ],
        TESTING=True
    )

@pytest.fixture(scope="session")
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}

# Import component-specific fixtures
pytest_plugins = [
    "tests.fixtures.redis_fixtures",
    "tests.fixtures.async_fixtures",
    "tests.fixtures.agent_fixtures",
    "tests.fixtures.llm_fixtures",
]
