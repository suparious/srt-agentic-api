from typing import List, Dict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API settings
    API_KEY: str
    API_VERSION: str = "v1"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

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
    LLM_PROVIDER_CONFIGS: Dict[str, Dict[str, str]] = {
        "openai": {
            "api_base": OPENAI_API_BASE,
            "api_key": OPENAI_API_KEY,
        },
        "vllm": {
            "api_base": VLLM_API_BASE,
        },
        "llamacpp": {
            "api_base": LLAMACPP_API_BASE,
        },
        "tgi": {
            "api_base": TGI_API_BASE,
        },
    }

    # Agent settings
    MAX_AGENTS_PER_USER: int = 5
    DEFAULT_AGENT_MEMORY_LIMIT: int = 1000

    # Memory settings
    SHORT_TERM_MEMORY_TTL: int = 3600  # 1 hour in seconds
    LONG_TERM_MEMORY_LIMIT: int = 10000

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
