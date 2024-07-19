from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    CHROMA_PERSIST_DIRECTORY: str = "/path/to/persist"
    LOG_DIR: str = "/path/to/logs"

    class Config:
        env_file = ".env"

settings = Settings()
