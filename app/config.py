import os
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    API_KEY: str
    API_VERSION: str = "v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

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
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    VLLM_API_BASE: str = "https://artemis.hq.solidrust.net/v1"
    LLAMACPP_API_BASE: str = "http://llamacpp-server-endpoint"
    TGI_API_BASE: str = "http://tgi-server-endpoint"
    ANTHROPIC_API_KEY: str = ""  # Added Anthropic API Key

    # LLM Provider configurations
    LLM_PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {}

    @field_validator("LLM_PROVIDER_CONFIGS", mode="before")
    @classmethod
    def set_llm_provider_configs(cls, v: Any, info: Any) -> Dict[str, Dict[str, str]]:
        return {
            "openai": {
                "api_base": info.data.get("OPENAI_API_BASE"),
                "api_key": info.data.get("OPENAI_API_KEY"),
            },
            "vllm": {
                "api_base": info.data.get("VLLM_API_BASE"),
            },
            "llamacpp": {
                "api_base": info.data.get("LLAMACPP_API_BASE"),
            },
            "tgi": {
                "api_base": info.data.get("TGI_API_BASE"),
            },
            "anthropic": {
                "api_key": info.data.get("ANTHROPIC_API_KEY"),
            },
        }

    # Agent settings
    MAX_AGENTS_PER_USER: int = 5
    DEFAULT_AGENT_MEMORY_LIMIT: int = 1000

    # Memory settings
    SHORT_TERM_MEMORY_TTL: int = 3600  # 1 hour in seconds
    LONG_TERM_MEMORY_LIMIT: int = 10000

    model_config = SettingsConfigDict(
        env_file=".env" if not os.getenv("TESTING") else ".env.test",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
