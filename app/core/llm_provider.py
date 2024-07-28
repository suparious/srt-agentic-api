import asyncio
import aiohttp
import json
from typing import Dict, Any
from abc import ABC, abstractmethod
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.utils.logging import llm_logger

class LLMProviderException(Exception):
    """Base exception class for LLM provider errors."""

class APICallException(LLMProviderException):
    """Exception raised when an API call fails."""

class ResponseParsingException(LLMProviderException):
    """Exception raised when parsing the API response fails."""

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(APICallException),
    reraise=True
)
async def make_api_call(session, url, headers, data):
    try:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status != 200:
                error_content = await response.text()
                raise APICallException(f"API call failed: {response.status} - {error_content}")
            return await response.json()
    except aiohttp.ClientError as e:
        raise APICallException(f"API call failed due to client error: {str(e)}")

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']
        self.api_key = config.get('api_key') or settings.OPENAI_API_KEY

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(session, f"{self.api_base}/chat/completions", headers, data)
                return result['choices'][0]['message']['content']
        except APICallException as e:
            llm_logger.error(f"OpenAI API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing OpenAI API response: {str(e)}")
            raise ResponseParsingException(f"Failed to parse OpenAI API response: {str(e)}")

class VLLMProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(session, f"{self.api_base}/generate", headers, data)
                return result['text']
        except APICallException as e:
            llm_logger.error(f"vLLM API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing vLLM API response: {str(e)}")
            raise ResponseParsingException(f"Failed to parse vLLM API response: {str(e)}")

class LlamaCppServerProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": ["\n"]  # Add appropriate stop tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(session, f"{self.api_base}/completion", headers, data)
                return result['choices'][0]['text']
        except APICallException as e:
            llm_logger.error(f"Llama.cpp server API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing Llama.cpp server API response: {str(e)}")
            raise ResponseParsingException(f"Failed to parse Llama.cpp server API response: {str(e)}")

class TGIServerProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "do_sample": True
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(session, f"{self.api_base}/generate", headers, data)
                return result['generated_text']
        except APICallException as e:
            llm_logger.error(f"TGI server API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing TGI server API response: {str(e)}")
            raise ResponseParsingException(f"Failed to parse TGI server API response: {str(e)}")

class LLMProvider:
    def __init__(self, provider_config: Dict[str, Any]):
        self.provider_type = provider_config['provider_type']
        self.config = provider_config
        self.config['api_base'] = self.config.get('api_base') or settings.LLM_PROVIDER_CONFIGS.get(self.provider_type, {}).get('api_base')
        self.provider = self._get_provider()

    def _get_provider(self) -> BaseLLMProvider:
        if self.provider_type == "openai":
            return OpenAIProvider(self.config)
        elif self.provider_type == "vllm":
            return VLLMProvider(self.config)
        elif self.provider_type == "llamacpp":
            return LlamaCppServerProvider(self.config)
        elif self.provider_type == "tgi":
            return TGIServerProvider(self.config)
        else:
            raise ValueError(f"Unsupported provider type: {self.provider_type}")

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        return await self.provider.generate(prompt, temperature, max_tokens)

# Factory function to create LLMProvider instances
def create_llm_provider(provider_config: Dict[str, Any]) -> LLMProvider:
    return LLMProvider(provider_config)
