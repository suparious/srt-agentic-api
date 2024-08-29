import pytest
from unittest.mock import AsyncMock, MagicMock
from app.core.llm_provider import LLMProvider

@pytest.fixture
def mock_llm_response():
    return {
        "choices": [
            {
                "text": "This is a mock LLM response.",
                "finish_reason": "stop"
            }
        ]
    }

@pytest.fixture
def mock_llm_provider(mock_llm_response):
    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.generate.return_value = mock_llm_response
    return mock_provider

@pytest.fixture
def mock_llm_provider_factory(mock_llm_provider):
    def factory(provider_type: str, model_name: str):
        return mock_llm_provider
    return factory

@pytest.fixture(autouse=True)
async def llm_isolation(request):
    if "llm" in request.keywords:
        # Perform any necessary setup for LLM isolation
        yield
        # Perform any necessary cleanup for LLM isolation
    else:
        yield
