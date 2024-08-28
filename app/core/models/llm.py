from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional, Callable
from uuid import UUID, uuid4
from enum import Enum

class LLMProviderConfig(BaseModel):
    provider_type: str = Field(..., description="The LLM provider type (e.g., 'openai', 'vllm', 'llamacpp', 'tgi')")
    model_name: str = Field(..., description="The specific model name to use (e.g., 'gpt-4', 'claude-v1')")
    api_key: Optional[str] = Field(None, description="API key for the provider (if required)")
    api_base: Optional[str] = Field(None, description="Base URL for the provider's API (if custom)")

    model_config = ConfigDict(extra="forbid")
