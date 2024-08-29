import os
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from app.core.models.llm import LLMProviderConfig

class Settings(BaseSettings):
    API_KEY: str
    API_VERSION: str = "v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Database settings
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_PERSIST_DIRECTORY: str = "./data"
    TEST_REDIS_URL: str = "redis://localhost:6379/15"  # Use database 15 for testing
    TEST_CHROMA_PERSIST_DIRECTORY: str = "./test_chroma_db"

    # Testing flag
    TESTING: bool = False

    # Logging settings
    LOG_DIR: str = "./logs"
    LOG_LEVEL: str = "INFO"

    # LLM Provider settings
    DEFAULT_LLM_PROVIDER: str = "vllm"
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    VLLM_API_BASE: str = "https://artemis.hq.solidrust.net/v1"
    LLAMACPP_API_BASE: str = "http://llamacpp-server-endpoint"
    TGI_API_BASE: str = "http://tgi-server-endpoint"
    ANTHROPIC_API_KEY: str = ""  # Added Anthropic API Key

    # LLM Provider configurations
    LLM_PROVIDER_CONFIGS: List[LLMProviderConfig] = Field(default_factory=list)

    # Agent settings
    MAX_AGENTS_PER_USER: int = 5
    DEFAULT_AGENT_MEMORY_LIMIT: int = 1000

    # Memory settings
    SHORT_TERM_MEMORY_TTL: int = 3600  # 1 hour in seconds
    LONG_TERM_MEMORY_LIMIT: int = 10000
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Memory consolidation settings
    CONSOLIDATION_INTERVAL: int = 21600  # 6 hours in seconds
    CONSOLIDATION_IMPORTANCE_THRESHOLD: float = 0.7
    MAX_SHORT_TERM_MEMORIES: int = 1000  # Maximum number of short-term memories before forced consolidation

    @field_validator("LLM_PROVIDER_CONFIGS", mode="before")
    @classmethod
    def validate_llm_provider_configs(cls, v: Any, info: Any) -> List[LLMProviderConfig]:
        if isinstance(v, dict):
            return [LLMProviderConfig(**config) for config in v.values()]
        elif isinstance(v, list):
            return [LLMProviderConfig(**config) if isinstance(config, dict) else config for config in v]
        elif v is None or (isinstance(v, list) and len(v) == 0):
            # If LLM_PROVIDER_CONFIGS is not set or empty, create default configs
            return [
                LLMProviderConfig(
                    provider_type="openai",
                    model_name="gpt-3.5-turbo",
                    api_base=info.data.get("OPENAI_API_BASE"),
                    api_key=info.data.get("OPENAI_API_KEY"),
                ),
                LLMProviderConfig(
                    provider_type="vllm",
                    model_name="llama-7b",
                    api_base=info.data.get("VLLM_API_BASE"),
                ),
                LLMProviderConfig(
                    provider_type="llamacpp",
                    model_name="llama-13b",
                    api_base=info.data.get("LLAMACPP_API_BASE"),
                ),
                LLMProviderConfig(
                    provider_type="tgi",
                    model_name="tgi-model",
                    api_base=info.data.get("TGI_API_BASE"),
                ),
                LLMProviderConfig(
                    provider_type="anthropic",
                    model_name="claude-v1",
                    api_key=info.data.get("ANTHROPIC_API_KEY"),
                ),
            ]
        raise ValueError("LLM_PROVIDER_CONFIGS must be a list, a dict, or None")

    model_config = SettingsConfigDict(
        env_file=".env" if not os.getenv("TESTING") else ".env.test",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
