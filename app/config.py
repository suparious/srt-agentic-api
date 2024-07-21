import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # API settings
    API_KEY: str
    API_VERSION: str = "v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        print(f"Debug: ALLOWED_ORIGINS value received: {v}")
        print(f"Debug: ALLOWED_ORIGINS type: {type(v)}")
        print(f"Debug: ALLOWED_ORIGINS env var: {os.environ.get('ALLOWED_ORIGINS')}")

        if isinstance(v, str):
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, list):
            # Handle list of strings
            return [str(origin) for origin in v if origin]
        elif v is None:
            # Default to allowing all origins if not set
            return ["*"]
        else:
            raise ValueError(f"Invalid ALLOWED_ORIGINS format: {v}")

    # Database settings
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_PERSIST_DIRECTORY: str = "/path/to/persist"

    # Logging settings
    LOG_DIR: str = "/path/to/logs"
    LOG_LEVEL: str = "INFO"

    # LLM Provider settings
    DEFAULT_LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    ANTHROPIC_API_KEY: str = ""
    VLLM_API_BASE: str = "http://vllm-api-endpoint"
    LLAMACPP_API_BASE: str = "http://llamacpp-server-endpoint"
    TGI_API_BASE: str = "http://tgi-server-endpoint"

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
        }

    # Agent settings
    MAX_AGENTS_PER_USER: int = 5
    DEFAULT_AGENT_MEMORY_LIMIT: int = 1000

    # Memory settings
    SHORT_TERM_MEMORY_TTL: int = 3600  # 1 hour in seconds
    LONG_TERM_MEMORY_LIMIT: int = 10000

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "env_file_encoding": "utf-8",
    }

settings = Settings()
print(f"Debug: Final ALLOWED_ORIGINS value: {settings.ALLOWED_ORIGINS}")
