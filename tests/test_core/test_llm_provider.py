import pytest
from unittest.mock import AsyncMock, patch
from app.core.llm_provider import LLMProvider, OpenAIProvider, VLLMProvider, LlamaCppServerProvider, APICallException


@pytest.fixture
def provider_configs():
    return [
        {
            "provider_type": "openai",
            "model_name": "gpt-3.5-turbo",
            "api_key": "test-key"
        },
        {
            "provider_type": "vllm",
            "model_name": "llama-7b",
            "api_base": "http://vllm-server:8000"
        },
        {
            "provider_type": "llamacpp",
            "model_name": "llama-13b",
            "api_base": "http://llamacpp-server:8080"
        }
    ]


@pytest.mark.asyncio
async def test_llm_provider_fallback(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai, \
            patch('app.core.llm_provider.VLLMProvider.generate') as mock_vllm, \
            patch('app.core.llm_provider.LlamaCppServerProvider.generate') as mock_llamacpp:
        mock_openai.side_effect = APICallException("OpenAI failed")
        mock_vllm.side_effect = APICallException("vLLM failed")
        mock_llamacpp.return_value = "LlamaCpp response"

        llm_provider = LLMProvider(provider_configs)
        result = await llm_provider.generate("Test prompt", 0.7, 100)

        assert result == "LlamaCpp response"
        mock_openai.assert_called_once()
        mock_vllm.assert_called_once()
        mock_llamacpp.assert_called_once()


@pytest.mark.asyncio
async def test_llm_provider_all_fail(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai, \
            patch('app.core.llm_provider.VLLMProvider.generate') as mock_vllm, \
            patch('app.core.llm_provider.LlamaCppServerProvider.generate') as mock_llamacpp:
        mock_openai.side_effect = APICallException("OpenAI failed")
        mock_vllm.side_effect = APICallException("vLLM failed")
        mock_llamacpp.side_effect = APICallException("LlamaCpp failed")

        llm_provider = LLMProvider(provider_configs)

        with pytest.raises(APICallException, match="LlamaCpp failed"):
            await llm_provider.generate("Test prompt", 0.7, 100)

        mock_openai.assert_called_once()
        mock_vllm.assert_called_once()
        mock_llamacpp.assert_called_once()


@pytest.mark.asyncio
async def test_llm_provider_first_succeeds(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai:
        mock_openai.return_value = "OpenAI response"

        llm_provider = LLMProvider(provider_configs)
        result = await llm_provider.generate("Test prompt", 0.7, 100)

        assert result == "OpenAI response"
        mock_openai.assert_called_once()
