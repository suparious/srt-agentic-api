import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from app.core.models.llm import LLMProviderConfig
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from app.utils.logging import llm_logger
from cachetools import TTLCache
from asyncio import Semaphore

request_cache = TTLCache(maxsize=1000, ttl=300)
rate_limiter = Semaphore(10)

class LLMProviderException(Exception):
    """Base exception class for LLM provider errors."""


class APICallException(LLMProviderException):
    """Exception raised when an API call fails."""


class ResponseParsingException(LLMProviderException):
    """Exception raised when parsing the API response fails."""


class ProviderConfig(BaseModel):
    provider_type: str
    model_name: str
    api_base: str
    api_key: Optional[str] = None


class ProviderResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(APICallException),
    reraise=True,
)
async def make_api_call(
    session: aiohttp.ClientSession,
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    timeout: float = 30.0,  # Add timeout parameter
) -> Dict[str, Any]:
    try:
        async with session.post(url, headers=headers, json=data, timeout=timeout) as response:
            if response.status != 200:
                error_content = await response.text()
                raise APICallException(
                    f"API call failed: {response.status} - {error_content}"
                )
            return await response.json()
    except asyncio.TimeoutError:
        raise APICallException("API call timed out")
    except aiohttp.ClientError as e:
        raise APICallException(f"API call failed due to client error: {str(e)}")



class BaseLLMProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> ProviderResponse:
        pass

    async def _rate_limited_generate(self, prompt: str, temperature: float, max_tokens: int) -> ProviderResponse:
        async with rate_limiter:
            return await self.generate(prompt, temperature, max_tokens)


class OpenAIProvider(BaseLLMProvider):
    async def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> ProviderResponse:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": self.config.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(
                    session, f"{self.config.api_base}/chat/completions", headers, data
                )
                return ProviderResponse(
                    content=result["choices"][0]["message"]["content"],
                    metadata={"provider": "openai", "model": self.config.model_name},
                )
        except APICallException as e:
            llm_logger.error(f"OpenAI API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing OpenAI API response: {str(e)}")
            raise ResponseParsingException(
                f"Failed to parse OpenAI API response: {str(e)}"
            )


class VLLMProvider(BaseLLMProvider):
    async def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> ProviderResponse:
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.config.model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(
                    session, f"{self.config.api_base}/generate", headers, data
                )
                return ProviderResponse(
                    content=result["text"],
                    metadata={"provider": "vllm", "model": self.config.model_name},
                )
        except APICallException as e:
            llm_logger.error(f"vLLM API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing vLLM API response: {str(e)}")
            raise ResponseParsingException(
                f"Failed to parse vLLM API response: {str(e)}"
            )


class LlamaCppServerProvider(BaseLLMProvider):
    async def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> ProviderResponse:
        headers = {"Content-Type": "application/json"}
        data = {
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stop": ["\n"],  # Add appropriate stop tokens
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(
                    session, f"{self.config.api_base}/completion", headers, data
                )
                return ProviderResponse(
                    content=result["choices"][0]["text"],
                    metadata={"provider": "llamacpp", "model": self.config.model_name},
                )
        except APICallException as e:
            llm_logger.error(f"Llama.cpp server API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing Llama.cpp server API response: {str(e)}")
            raise ResponseParsingException(
                f"Failed to parse Llama.cpp server API response: {str(e)}"
            )


class TGIServerProvider(BaseLLMProvider):
    async def generate(
        self, prompt: str, temperature: float, max_tokens: int
    ) -> ProviderResponse:
        headers = {"Content-Type": "application/json"}
        data = {
            "inputs": prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "do_sample": True,
            },
        }

        try:
            async with aiohttp.ClientSession() as session:
                result = await make_api_call(
                    session, f"{self.config.api_base}/generate", headers, data
                )
                return ProviderResponse(
                    content=result["generated_text"],
                    metadata={"provider": "tgi", "model": self.config.model_name},
                )
        except APICallException as e:
            llm_logger.error(f"TGI server API call failed: {str(e)}")
            raise
        except KeyError as e:
            llm_logger.error(f"Error parsing TGI server API response: {str(e)}")
            raise ResponseParsingException(
                f"Failed to parse TGI server API response: {str(e)}"
            )


class LLMProvider:
    def __init__(self, provider_configs: List[LLMProviderConfig]):
        self.providers = [self._get_provider(config) for config in provider_configs]

    def _get_provider(self, config: LLMProviderConfig) -> BaseLLMProvider:
        # Existing implementation...
        pass

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        # Check cache first
        cache_key = (prompt, temperature, max_tokens)
        if cache_key in request_cache:
            return request_cache[cache_key]

        for provider in self.providers:
            try:
                response = await provider._rate_limited_generate(prompt, temperature, max_tokens)
                # Cache the successful response
                request_cache[cache_key] = response
                return response
            except Exception as e:
                llm_logger.warning(f"Provider {provider.__class__.__name__} failed: {str(e)}")
        raise Exception("All providers failed")


def create_llm_provider() -> LLMProvider:
    provider_configs = [
        LLMProviderConfig(
            provider_type=config.provider_type,
            model_name=config.model_name,
            api_base=config.api_base,
            api_key=config.api_key
        ) for config in settings.LLM_PROVIDER_CONFIGS
    ]
    return LLMProvider(provider_configs)
