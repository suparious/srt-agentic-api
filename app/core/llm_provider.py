import asyncio
import aiohttp
import json
from typing import Dict, Any
from abc import ABC, abstractmethod
from app.config import settings

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

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/chat/completions", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_content = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_content}")

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

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/generate", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['text']
                else:
                    error_content = await response.text()
                    raise Exception(f"vLLM API error: {response.status} - {error_content}")

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

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.api_base}/completion", headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['text']
                else:
                    error_content = await response.text()
                    raise Exception(f"Llama.cpp server API error: {response.status} - {error_content}")

class TGIServerProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        # Implement TGI server API call here
        # This is a placeholder implementation
        await asyncio.sleep(1)  # Simulating API call
        return f"Response from TGI model {self.model_name}: {prompt[:30]}..."

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