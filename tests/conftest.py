import pytest
from httpx import AsyncClient
from app.main import app
from app.config import Settings

@pytest.fixture
def test_settings():
    return Settings(
        API_KEY="test_api_key",
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],  # Set as a list
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
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}
