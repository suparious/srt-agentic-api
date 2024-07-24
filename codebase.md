# requirements.txt

```txt
fastapi>=0.95.2,<1.0.0
uvicorn>=0.22.0,<1.0.0
pydantic>=2.0.3,<3.0.0
pydantic-settings>=2.0.2,<3.0.0
python-dotenv>=1.0.0,<2.0.0
redis>=5.0.0,<6.0.0
chromadb>=0.3.26,<1.0.0
asyncio
httpx>=0.24.1,<1.0.0
python-multipart>=0.0.6,<1.0.0
PyJWT>=2.7.0,<3.0.0
bcrypt>=4.0.1,<5.0.0
loguru>=0.7.0,<1.0.0
tenacity>=8.2.2,<9.0.0

```

# requirements-testing.txt

```txt
# additional unit testing requirements:
pytest>=7.3.1,<8.0.0
pytest-asyncio
httpx>=0.24.1,<1.0.0
pytest-cov
```

# pytest.ini

```ini
[pytest]
asyncio_mode = auto
env_files = .env.test

```

# docker-compose.yml

```yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - VALKEY_HOST=valkey
      - DEBUG_MODE=false
    depends_on:
      - valkey
    volumes:
      - .:/app

  valkey:
    image: docker.io/valkey/valkey:latest
    environment:
      - ALLOW_EMPTY_PASSWORD=yes  # Recommended only for development
      - VALKEY_DISABLE_COMMANDS=FLUSHDB,FLUSHALL
    ports:
      - "6379:6379"
    command: valkey-server --appendonly yes
    volumes:
      - valkey_data:/data

volumes:
  valkey_data:
    driver: local

```

# TESTING.md

```md
# Instructions for Running Tests

1. Open a terminal window.
2. Navigate to the root directory of the srt-agentic-api project.
3. Ensure that all dependencies are installed by running:
   \`\`\`
   pip install -r requirements.txt
   pip install -r requirements-testing.txt
   \`\`\`
4. Run the following command to execute the tests and capture the output:
   \`\`\`
   pytest --verbose --capture=no --cov=app --cov-report=term-missing > logs/test_results_detailed.txt
   #pytest --verbose --capture=no > logs/test_results_detailed.txt
   \`\`\`
5. Once the command completes, please provide the contents of the `logs/test_results_detailed.txt` file as an artifact in your next message.

Note: If you encounter any errors or issues while running the tests, please include those details in your response as well.
```

# README.md

```md
# SolidRusT Agentic API

SolidRusT Agentic API is a powerful and flexible API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, including memory management, function execution, and message processing.

## Key Features

- Agent creation and management
- Short-term (Redis) and long-term (ChromaDB) memory systems
- Function calling capabilities
- Flexible LLM provider integration
- Scalable architecture

## Project Structure

\`\`\`plaintext
srt-agentic-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── endpoints/
│   │   └── models/
│   ├── core/
│   └── utils/
├── docs/
├── logs/
├── tests/
├── requirements.txt
├── Dockerfile
└── README.md
\`\`\`

## Setup Instructions

1. Clone the repository:
   \`\`\`
   git clone https://github.com/SolidRusT/srt-agentic-api.git
   cd srt-agentic-api
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   \`\`\`

3. Install the required dependencies:
   \`\`\`
   pip install -r requirements.txt
   \`\`\`

4. Copy the `.env.example` file to `.env` and update the values:
   \`\`\`
   cp .env.example .env
   \`\`\`
   Edit the `.env` file with your specific configuration values.

5. Set up the database:
   - Ensure Redis is running for short-term memory operations.
   - Set up ChromaDB for long-term memory operations.

## Running the Application

To run the application locally:

\`\`\`
uvicorn app.main:app --reload
\`\`\`

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Development

### Running Tests

To run the test suite:

\`\`\`
pytest
\`\`\`

### Adding New Endpoints

1. Create a new file in `app/api/endpoints/` for your endpoint.
2. Define the necessary models in `app/api/models/`.
3. Implement the core logic in `app/core/` if needed.
4. Update `app/main.py` to include your new endpoint router.

### Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and write tests if applicable.
4. Run the test suite to ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## Docker

To build and run the Docker container:

\`\`\`
docker build -t srt-agentic-api .
docker run -p 8000:8000 srt-agentic-api
\`\`\`

```

# Dockerfile

```
# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

```

# .gitignore

```
.env
/.venv/
/__pycache__/
/logs/
/data/

```

# .coverage

This is a binary file of the type: Binary

# .aidigestignore

```
.env
/.git/
/.venv/
/__pycache__/
/.pytest_cache/
/.idea/
/data/
/logs/
/docs/

```

# tests/conftest.py

```py
import os
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.config import Settings
from app.api.models.agent import AgentConfig, MemoryConfig
from dotenv import load_dotenv

# Load the test environment variables
load_dotenv('.env.test')

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        API_KEY=os.getenv('API_KEY', 'your_api_key_here'),  # Use the API key from .env.test
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],
        REDIS_URL="redis://localhost:6379/15",
        CHROMA_PERSIST_DIRECTORY="./test_chroma_db",
        OPENAI_API_KEY="test_openai_key",
        ANTHROPIC_API_KEY="test_anthropic_key",
        VLLM_API_BASE="http://test-vllm-api-endpoint",
        LLAMACPP_API_BASE="http://test-llamacpp-server-endpoint",
        TGI_API_BASE="http://test-tgi-server-endpoint",
        TESTING=True
    )

@pytest.fixture(scope="module")
def test_app(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
def sync_client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="module")
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}

@pytest.fixture
async def test_agent(async_client, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": AgentConfig(
            llm_provider="openai",
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(
                use_long_term_memory=True,
                use_redis_cache=True
            )
        ).model_dump(),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ).model_dump(),
        "initial_prompt": "You are a helpful assistant."
    }
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    return response.json()["agent_id"]

```

# tests/__init__.py

```py

```

# tests/README.md

```md
# SolidRusT Agentic API Tests

This directory contains the tests for the SolidRusT Agentic API. The tests are organized into two main categories: API tests and Core tests.

## Directory Structure

\`\`\`
tests/
├── __init__.py
├── conftest.py
├── README.md
├── test_api/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_function.py
│   ├── test_main.py
│   ├── test_memory.py
│   └── test_message.py
└── test_core/
    ├── __init__.py
    ├── test_agent.py
    └── test_memory.py
\`\`\`

- `conftest.py`: Contains pytest fixtures that can be used across multiple test files.
- `test_api/`: Contains tests for the API endpoints.
- `test_core/`: Contains tests for the core functionality of the application.

## Running Tests

To run all tests, use the following command from the root directory of the project:

\`\`\`
pytest
\`\`\`

To run tests in a specific file, use:

\`\`\`
pytest tests/path/to/test_file.py
\`\`\`

For example, to run the main API tests:

\`\`\`
pytest tests/test_api/test_main.py
\`\`\`

## Test Categories

### API Tests

These tests check the functionality of the API endpoints. They ensure that the API responds correctly to various requests and handles different scenarios appropriately.

### Core Tests

These tests focus on the internal logic and functionality of the application, independent of the API layer. They verify that the core components of the system work as expected.

## Writing New Tests

When adding new functionality to the API or core components, please add corresponding tests. Follow these guidelines:

1. Place API-related tests in the `test_api/` directory.
2. Place core functionality tests in the `test_core/` directory.
3. Use descriptive names for test functions, starting with `test_`.
4. Use pytest fixtures where appropriate to set up test environments.
5. Aim for high test coverage, including both happy paths and edge cases.

## Continuous Integration

These tests are run as part of our CI/CD pipeline. Ensure all tests pass locally before pushing changes to the repository.


## Comments

Now, let's address the warnings we're seeing in the test output:

1. For the Pydantic warning about the "model_name" field, you might want to review your Pydantic models and consider renaming any fields that start with "model_" to avoid conflicts.

2. The DeprecationWarnings about `google._upb._message` are likely coming from a dependency. For now, we can ignore these as they're not directly related to our code.

3. The Pydantic deprecation warning about class-based `config` suggests updating your Pydantic models to use `ConfigDict` instead of class-based config. This is a change introduced in Pydantic v2.

To address the Pydantic warnings, you may need to update your models. Here's an example of how to update a model using `ConfigDict`:

\`\`\`python
from pydantic import BaseModel, ConfigDict

class YourModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    # Your model fields here
    model_name: str  # This field name is now allowed
\`\`\`

To suppress warnings during tests (if you're not ready to address them immediately), you can add a `pytest.ini` file in the root of your project:

\`\`\`ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning:google._upb._message:
    ignore::pydantic.PydanticDeprecatedSince20
\`\`\`

This will suppress the DeprecationWarnings from Google protobuf and the Pydantic v2 migration warnings during test runs.

```

# app/main.py

```py
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("Python version:", sys.version)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())
print("Contents of current directory:", os.listdir())
print("Initializing FastAPI app")

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from app.api.endpoints import agent, message, function, memory
from app.utils.auth import get_api_key
from app.utils.logging import main_logger
from app.config import settings

app = FastAPI(
    title="SolidRusT Agentic API",
    description="A powerful and flexible API for creating, managing, and interacting with AI agents.",
    version="1.0.0",
    contact={
        "name": "SolidRusT Team",
        "url": "https://github.com/SolidRusT/srt-agentic-api",
        "email": "support@solidrust.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SolidRusT Agentic API",
        version="1.0.0",
        description="A powerful and flexible API for creating, managing, and interacting with AI agents.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agent.router, prefix="/agent", tags=["Agents"])
app.include_router(message.router, prefix="/message", tags=["Messages"])
app.include_router(function.router, prefix="/function", tags=["Functions"])
app.include_router(memory.router, prefix="/memory", tags=["Memory"])

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint that welcomes users to the SolidRusT Agentic API.
    """
    return {"message": "Welcome to SolidRusT Agentic API"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    main_logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    main_logger.info(f"Response status code: {response.status_code}")
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    main_logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    main_logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )

if __name__ == "__main__":
    import uvicorn
    main_logger.info("Starting SolidRusT Agentic API")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)

```

# app/config.py

```py
import os
from typing import List, Dict, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
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
    TEST_REDIS_URL: str = "redis://localhost:6379/15"  # Use database 15 for testing
    TEST_CHROMA_PERSIST_DIRECTORY: str = "./test_chroma_db"

    # Testing flag
    TESTING: bool = False

    @property
    def redis_url(self):
        return self.TEST_REDIS_URL if self.TESTING else self.REDIS_URL

    @property
    def chroma_persist_directory(self):
        return self.TEST_CHROMA_PERSIST_DIRECTORY if self.TESTING else self.CHROMA_PERSIST_DIRECTORY

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

    model_config = SettingsConfigDict(
        env_file=".env" if not os.getenv("TESTING") else ".env.test",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()
print(f"Debug: Final ALLOWED_ORIGINS value: {settings.ALLOWED_ORIGINS}")

```

# app/__init__.py

```py

```

# tests/test_core/test_memory.py

```py
import pytest
from uuid import UUID
from unittest.mock import AsyncMock, patch
from app.core.memory import RedisMemory, VectorMemory, MemorySystem
from app.api.models.memory import MemoryType, MemoryEntry
from app.api.models.agent import MemoryConfig

@pytest.fixture
def memory_config():
    return MemoryConfig(use_long_term_memory=True, use_redis_cache=True)

@pytest.mark.asyncio
async def test_redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')

    with patch('app.core.memory.redis_memory.aioredis') as mock_redis:
        mock_redis_client = AsyncMock()
        mock_redis.from_url.return_value = mock_redis_client

        redis_memory = RedisMemory("redis://localhost:6379", agent_id)

        # Test add
        await redis_memory.add("test_key", "test_value")
        mock_redis_client.set.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key", "test_value", ex=3600)

        # Test get
        mock_redis_client.get.return_value = "test_value"
        value = await redis_memory.get("test_key")
        assert value == "test_value"
        mock_redis_client.get.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key")

        # Test delete
        await redis_memory.delete("test_key")
        mock_redis_client.delete.assert_called_once_with("agent:12345678-1234-5678-1234-567812345678:test_key")

@pytest.mark.asyncio
async def test_vector_memory():
    with patch('app.core.memory.vector_memory.chromadb') as mock_chromadb:
        mock_client = AsyncMock()
        mock_collection = AsyncMock()
        mock_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.Client.return_value = mock_client

        vector_memory = VectorMemory("test_collection", mock_chromadb.config.Settings())

        # Test add
        await vector_memory.add("test_id", "test_content", {"key": "value"})
        mock_collection.add.assert_called_once_with(documents=["test_content"], metadatas=[{"key": "value"}], ids=["test_id"])

        # Test search
        mock_collection.query.return_value = {
            "ids": [["test_id"]],
            "documents": [["test_content"]],
            "metadatas": [[{"key": "value"}]]
        }
        results = await vector_memory.search("test query")
        assert results == [{"id": "test_id", "content": "test_content", "metadata": {"key": "value"}}]
        mock_collection.query.assert_called_once_with(query_texts=["test query"], n_results=5)

@pytest.mark.asyncio
async def test_memory_system(memory_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')

    with patch('app.core.memory.memory_system.RedisMemory') as MockRedisMemory, \
            patch('app.core.memory.memory_system.VectorMemory') as MockVectorMemory:
        mock_redis = AsyncMock()
        mock_vector = AsyncMock()
        MockRedisMemory.return_value = mock_redis
        MockVectorMemory.return_value = mock_vector

        memory_system = MemorySystem(agent_id, memory_config)

        # Test add (short-term memory)
        await memory_system.add(MemoryType.SHORT_TERM, "test_content", {"key": "value"})
        mock_redis.add.assert_called_once()

        # Test add (long-term memory)
        await memory_system.add(MemoryType.LONG_TERM, "test_content", {"key": "value"})
        mock_vector.add.assert_called_once()

        # Test retrieve (short-term memory)
        mock_redis.get.return_value = "test_content"
        result = await memory_system.retrieve(MemoryType.SHORT_TERM, "test_id")
        assert result == MemoryEntry(content="test_content")

        # Test retrieve (long-term memory)
        mock_vector.search.return_value = [{"id": "test_id", "content": "test_content", "metadata": {"key": "value"}}]
        result = await memory_system.retrieve(MemoryType.LONG_TERM, "test_id")
        assert result == MemoryEntry(content="test_content", metadata={"key": "value"})

        # Test search
        results = await memory_system.search(MemoryType.LONG_TERM, "test query")
        assert results == [MemoryEntry(content="test_content", metadata={"key": "value"})]

        # Test delete
        await memory_system.delete(MemoryType.SHORT_TERM, "test_id")
        mock_redis.delete.assert_called_once()

@pytest.mark.asyncio
async def test_memory_system_integration(memory_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    memory_system = MemorySystem(agent_id, memory_config)

    # Test add and retrieve (short-term memory)
    short_term_id = await memory_system.add(MemoryType.SHORT_TERM, "short-term content")
    short_term_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert short_term_result.content == "short-term content"

    # Test add and retrieve (long-term memory)
    long_term_id = await memory_system.add(MemoryType.LONG_TERM, "long-term content", {"type": "test"})
    long_term_result = await memory_system.retrieve(MemoryType.LONG_TERM, long_term_id)
    assert long_term_result.content == "long-term content"
    assert long_term_result.metadata == {"type": "test"}

    # Test search
    search_results = await memory_system.search(MemoryType.LONG_TERM, "long-term")
    assert len(search_results) > 0
    assert search_results[0].content == "long-term content"

    # Test delete
    await memory_system.delete(MemoryType.SHORT_TERM, short_term_id)
    deleted_result = await memory_system.retrieve(MemoryType.SHORT_TERM, short_term_id)
    assert deleted_result is None

```

# tests/test_core/test_agent.py

```py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import UUID
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig


@pytest.fixture
def agent_config():
    return AgentConfig(
        llm_provider="openai",
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        )
    )


@pytest.mark.asyncio
async def test_agent_initialization(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        assert agent.id == agent_id
        assert agent.name == agent_name
        assert agent.config == agent_config
        assert isinstance(agent.llm_provider, AsyncMock)
        assert isinstance(agent.memory, AsyncMock)


@pytest.mark.asyncio
async def test_agent_process_message(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"
    test_message = "Hello, Agent!"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_llm_provider.generate.return_value = "Generated response"
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        mock_memory_system.retrieve_relevant.return_value = []
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        response, function_calls = await agent.process_message(test_message)

        assert response == "Generated response"
        assert function_calls == []
        mock_memory_system.retrieve_relevant.assert_called_once_with(test_message)
        mock_llm_provider.generate.assert_called_once()
        mock_memory_system.add.assert_called_once()


@pytest.mark.asyncio
async def test_agent_execute_function(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider') as mock_create_llm_provider, \
            patch('app.core.agent.MemorySystem') as MockMemorySystem:
        mock_llm_provider = AsyncMock()
        mock_create_llm_provider.return_value = mock_llm_provider

        mock_memory_system = AsyncMock()
        MockMemorySystem.return_value = mock_memory_system

        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        async def test_function(param1, param2):
            return f"Executed with {param1} and {param2}"

        mock_function = AsyncMock(side_effect=test_function)
        mock_function.id = "test_function_id"
        agent.get_function_by_name = Mock(return_value=mock_function)

        with patch.dict('app.core.agent.registered_functions', {"test_function_id": mock_function}):
            result = await agent.execute_function(
                function_name="test_function",
                parameters={"param1": "value1", "param2": "value2"}
            )

        assert result == "Executed with value1 and value2"
        agent.get_function_by_name.assert_called_once_with("test_function")
        mock_function.assert_awaited_once_with(param1="value1", param2="value2")


@pytest.mark.asyncio
async def test_agent_get_available_functions(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent_name = "Test Agent"

    with patch('app.core.agent.create_llm_provider'), patch('app.core.agent.MemorySystem'):
        agent = Agent(agent_id=agent_id, name=agent_name, config=agent_config, memory_config=agent_config.memory_config)

        mock_function1 = Mock(id="func1", name="Function 1")
        mock_function2 = Mock(id="func2", name="Function 2")

        with patch.dict('app.core.agent.registered_functions', {
            "func1": mock_function1,
            "func2": mock_function2
        }):
            agent.available_function_ids = ["func1", "func2"]
            available_functions = agent.get_available_functions()

        assert len(available_functions) == 2
        assert available_functions[0].name == "Function 1"
        assert available_functions[1].name == "Function 2"

```

# tests/test_core/__init__.py

```py

```

# tests/test_api/test_message.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

async def test_send_message(async_client: AsyncClient, auth_headers, test_agent):
    message_data = {
        "agent_id": test_agent,
        "content": "Hello, agent!"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "agent_id" in result
    assert result["agent_id"] == test_agent
    assert "content" in result
    assert isinstance(result["content"], str)
    assert isinstance(result.get("function_calls", []), list)
    return result

async def test_get_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.get(f"/message/history?agent_id={test_agent}&limit=10", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert "agent_id" in history
    assert history["agent_id"] == test_agent
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    assert history["messages"][0]["content"] == "Hello, agent!"

async def test_clear_message_history(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.post(f"/message/clear", json={"agent_id": test_agent}, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Message history cleared successfully"

    # Verify that the history is indeed cleared
    response = await async_client.get(f"/message/history?agent_id={test_agent}&limit=10", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history["messages"]) == 0

async def test_get_latest_message(async_client: AsyncClient, auth_headers, test_agent):
    # First, send a message
    sent_message = await test_send_message(async_client, auth_headers, test_agent)

    response = await async_client.get(f"/message/latest?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    latest_message = response.json()
    assert latest_message["content"] == "Hello, agent!"

async def test_send_message_invalid_agent(async_client: AsyncClient, auth_headers):
    invalid_agent_id = str(UUID(int=0))
    message_data = {
        "agent_id": invalid_agent_id,
        "content": "This should fail"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

```

# tests/test_api/test_memory.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.memory import MemoryType, MemoryOperation

pytestmark = pytest.mark.asyncio

async def test_add_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "entry": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert "memory_id" in added_memory
    assert added_memory["message"] == "Memory added successfully"
    return added_memory["memory_id"]

async def test_retrieve_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    response = await async_client.get(f"/memory/retrieve?agent_id={test_agent}&memory_type={MemoryType.SHORT_TERM}&memory_id={memory_id}", headers=auth_headers)
    assert response.status_code == 200
    memory = response.json()
    assert memory["content"] == "Test memory content"
    assert memory["metadata"] == {"key": "value"}

async def test_search_memory(async_client: AsyncClient, auth_headers, test_agent):
    await test_add_memory(async_client, auth_headers, test_agent)  # Add a memory to search for
    search_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.SHORT_TERM,
        "query": "Test memory",
        "limit": 5
    }
    response = await async_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert "results" in results
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0

async def test_delete_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_id = await test_add_memory(async_client, auth_headers, test_agent)
    response = await async_client.delete(f"/memory/delete?agent_id={test_agent}&memory_type={MemoryType.SHORT_TERM}&memory_id={memory_id}", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Memory deleted successfully"

async def test_memory_operation(async_client: AsyncClient, auth_headers, test_agent):
    operation_data = {
        "agent_id": test_agent,
        "operation": MemoryOperation.ADD,
        "memory_type": MemoryType.SHORT_TERM,
        "data": {
            "content": "Test operation memory content",
            "metadata": {"operation": "test"}
        }
    }
    response = await async_client.post("/memory/operate", json=operation_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "ADD operation completed successfully"
    assert "result" in result

async def test_add_long_term_memory(async_client: AsyncClient, auth_headers, test_agent):
    memory_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.LONG_TERM,
        "entry": {
            "content": "Long-term test memory content",
            "metadata": {"key": "long_term_value"}
        }
    }
    response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert "memory_id" in added_memory
    assert added_memory["message"] == "Memory added successfully"

async def test_search_long_term_memory(async_client: AsyncClient, auth_headers, test_agent):
    await test_add_long_term_memory(async_client, auth_headers, test_agent)
    search_data = {
        "agent_id": test_agent,
        "memory_type": MemoryType.LONG_TERM,
        "query": "Long-term test",
        "limit": 5
    }
    response = await async_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert "results" in results
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0
    assert "Long-term test memory content" in results["results"][0]["content"]

```

# tests/test_api/test_main.py

```py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_read_main(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SolidRusT Agentic API"}
```

# tests/test_api/test_function.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

async def test_register_function(async_client: AsyncClient, auth_headers):
    function_data = {
        "function": {
            "name": "test_function",
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                }
            },
            "return_type": "string"
        }
    }
    response = await async_client.post("/function/register", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    registered_function = response.json()
    assert "function_id" in registered_function
    assert registered_function["message"] == "Function registered successfully"
    return registered_function["function_id"]

async def test_get_function(async_client: AsyncClient, auth_headers):
    function_id = await test_register_function(async_client, auth_headers)
    response = await async_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    get_function = response.json()
    assert get_function["name"] == "test_function"
    assert get_function["description"] == "A test function"

async def test_update_function(async_client: AsyncClient, auth_headers):
    function_id = await test_register_function(async_client, auth_headers)
    update_data = {
        "function_id": function_id,
        "updated_function": {
            "name": "updated_test_function",
            "description": "An updated test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"},
                    "param3": {"type": "boolean"}
                }
            },
            "return_type": "string"
        }
    }
    response = await async_client.put("/function/update", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_function = response.json()
    assert updated_function["message"] == "Function updated successfully"

async def test_delete_function(async_client: AsyncClient, auth_headers, test_agent):
    function_id = await test_register_function(async_client, auth_headers)
    response = await async_client.delete(f"/function/{function_id}?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Function removed successfully"

async def test_list_functions(async_client: AsyncClient, auth_headers, test_agent):
    # Register a couple of functions first
    await test_register_function(async_client, auth_headers)
    await test_register_function(async_client, auth_headers)

    response = await async_client.get(f"/function/available?agent_id={test_agent}", headers=auth_headers)
    assert response.status_code == 200
    functions = response.json()
    assert "functions" in functions
    assert isinstance(functions["functions"], list)
    assert len(functions["functions"]) >= 2  # We should have at least the two functions we just registered

async def test_execute_function(async_client: AsyncClient, auth_headers, test_agent):
    function_id = await test_register_function(async_client, auth_headers)
    execution_data = {
        "agent_id": test_agent,
        "function_name": "test_function",
        "parameters": {
            "param1": "test",
            "param2": 123
        }
    }
    response = await async_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result

async def test_execute_nonexistent_function(async_client: AsyncClient, auth_headers, test_agent):
    execution_data = {
        "agent_id": test_agent,
        "function_name": "nonexistent_function",
        "parameters": {}
    }
    response = await async_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

```

# tests/test_api/test_agent.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

async def test_create_agent(async_client: AsyncClient, auth_headers):
    agent_data = {
        "agent_name": "New Test Agent",
        "agent_config": {
            "llm_provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150,
            "memory_config": {
                "use_long_term_memory": True,
                "use_redis_cache": True
            }
        },
        "memory_config": {
            "use_long_term_memory": True,
            "use_redis_cache": True
        },
        "initial_prompt": "You are a helpful assistant."
    }
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    created_agent = response.json()
    assert "agent_id" in created_agent
    assert UUID(created_agent["agent_id"])

async def test_get_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["agent_id"] == test_agent
    assert agent["name"] == "Test Agent"

async def test_update_agent(async_client: AsyncClient, auth_headers, test_agent):
    update_data = {
        "agent_config": {
            "temperature": 0.8
        }
    }
    response = await async_client.patch(f"/agent/{test_agent}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["message"] == "Agent updated successfully"

async def test_delete_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.delete(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 204

async def test_list_agents(async_client: AsyncClient, auth_headers, test_agent):
    # Create a second agent to ensure we have at least two
    await test_create_agent(async_client, auth_headers)

    response = await async_client.get("/agent", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) >= 2  # We should have at least the two agents we created

```

# tests/test_api/__init__.py

```py

```

# app/core/llm_provider.py

```py
import asyncio
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
        # You might want to add API key handling here, e.g.:
        # self.api_key = config['api_key']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        # Implement OpenAI API call here
        # This is a placeholder implementation
        await asyncio.sleep(1)  # Simulating API call
        return f"Response from OpenAI model {self.model_name}: {prompt[:30]}..."

class VLLMProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        # Implement vLLM API call here
        # This is a placeholder implementation
        await asyncio.sleep(1)  # Simulating API call
        return f"Response from vLLM model {self.model_name}: {prompt[:30]}..."

class LlamaCppServerProvider(BaseLLMProvider):
    def __init__(self, config: Dict[str, Any]):
        self.model_name = config['model_name']
        self.api_base = config['api_base']

    async def generate(self, prompt: str, temperature: float, max_tokens: int) -> str:
        # Implement Llama.cpp server API call here
        # This is a placeholder implementation
        await asyncio.sleep(1)  # Simulating API call
        return f"Response from Llama.cpp model {self.model_name}: {prompt[:30]}..."

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

```

# app/core/agent.py

```py
import inspect
import asyncio
from uuid import UUID, uuid4
from typing import Dict, Any, Tuple, List, Optional
from app.api.models.agent import AgentConfig, MemoryConfig, AgentInfoResponse
from app.api.models.function import FunctionDefinition
from app.api.models.memory import MemoryType
from app.core.llm_provider import create_llm_provider
from app.core.memory import MemorySystem
from app.utils.logging import agent_logger
from fastapi import HTTPException

class Agent:
    def __init__(self, agent_id: UUID, name: str, config: AgentConfig, memory_config: MemoryConfig):
        self.id = agent_id
        self.name = name
        self.config = config
        self.llm_provider = create_llm_provider({
            'provider_type': config.llm_provider,
            'model_name': config.model_name
        })
        self.memory = MemorySystem(agent_id, memory_config)
        self.conversation_history = []
        self.available_function_ids: List[str] = []
        agent_logger.info(f"Agent {self.name} (ID: {self.id}) initialized with {config.llm_provider} provider")

    async def process_message(self, message: str) -> Tuple[str, List[Dict[str, Any]]]:
        try:
            agent_logger.info(f"Processing message for Agent {self.name} (ID: {self.id})")
            self.conversation_history.append({"role": "user", "content": message})

            relevant_context = await self.memory.retrieve_relevant(message)
            prompt = self._prepare_prompt(relevant_context)

            response = await self.llm_provider.generate(prompt, self.config.temperature, self.config.max_tokens)
            response_text, function_calls = self._parse_response(response)

            self.conversation_history.append({"role": "assistant", "content": response_text})
            await self.memory.add(MemoryType.SHORT_TERM, response_text, {"type": "assistant_response"})

            agent_logger.info(f"Message processed successfully for Agent {self.name} (ID: {self.id})")
            return response_text, function_calls
        except Exception as e:
            agent_logger.error(f"Error processing message for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

    async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
        try:
            agent_logger.info(f"Executing function {function_name} for Agent {self.name} (ID: {self.id})")
            get_function = self.get_function_by_name(function_name)
            if not get_function:
                raise ValueError(f"Unknown function: {function_name}")

            func_impl = registered_functions[get_function.id].implementation

            result = await func_impl(**parameters)

            agent_logger.info(f"Function {function_name} executed successfully for Agent {self.name} (ID: {self.id})")
            return result
        except Exception as e:
            agent_logger.error(f"Error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(e)}")
            raise

    def get_available_functions(self) -> List[FunctionDefinition]:
        return [registered_functions[func_id] for func_id in self.available_function_ids if func_id in registered_functions]

    def add_function(self, function_id: str):
        if function_id not in registered_functions:
            raise ValueError(f"Function with ID {function_id} is not registered")
        if function_id not in self.available_function_ids:
            self.available_function_ids.append(function_id)
            agent_logger.info(f"Function {registered_functions[function_id].name} added for Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(f"Function {registered_functions[function_id].name} already available for Agent {self.name} (ID: {self.id})")

    def remove_function(self, function_id: str):
        if function_id in self.available_function_ids:
            self.available_function_ids.remove(function_id)
            agent_logger.info(f"Function {registered_functions[function_id].name} removed from Agent {self.name} (ID: {self.id})")
        else:
            agent_logger.warning(f"Attempted to remove non-existent function {function_id} from Agent {self.name} (ID: {self.id})")

    def get_function_by_name(self, function_name: str) -> Optional[FunctionDefinition]:
        for func_id in self.available_function_ids:
            if func_id in registered_functions and registered_functions[func_id].name == function_name:
                return registered_functions[func_id]
        return None

    def _prepare_prompt(self, context: List[Dict[str, Any]]) -> str:
        context_str = "\n".join([f"Context: {item['content']}" for item in context])
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-5:]])
        return f"{context_str}\n\nConversation History:\n{history}\n\nAssistant:"

    def _parse_response(self, response: str) -> Tuple[str, List[Dict[str, Any]]]:
        function_calls = []
        if "FUNCTION CALL:" in response:
            parts = response.split("FUNCTION CALL:")
            response = parts[0].strip()
            for call in parts[1:]:
                try:
                    function_name, args = call.split("(", 1)
                    args = args.rsplit(")", 1)[0]
                    function_calls.append({
                        "name": function_name.strip(),
                        "arguments": eval(f"dict({args})")
                    })
                except Exception as e:
                    agent_logger.warning(f"Error parsing function call for Agent {self.name} (ID: {self.id}): {str(e)}")
        return response, function_calls

# Global dictionaries
agents: Dict[UUID, Agent] = {}
registered_functions: Dict[str, FunctionDefinition] = {}

# Facade functions for interacting with agents
async def create_agent(name: str, config: Dict[str, Any], memory_config: Dict[str, Any], initial_prompt: str) -> UUID:
    try:
        agent_id = uuid4()
        agent_config = AgentConfig(**config)
        mem_config = MemoryConfig(**memory_config)
        agent = Agent(agent_id, name, agent_config, mem_config)
        agents[agent_id] = agent
        await agent.process_message(initial_prompt)
        agent_logger.info(f"Agent {name} (ID: {agent_id}) created successfully")
        return agent_id
    except Exception as e:
        agent_logger.error(f"Error creating Agent {name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")

async def get_agent_info(agent_id: UUID) -> Optional[AgentInfoResponse]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.warning(f"No agent found with id: {agent_id}")
        return None

    return AgentInfoResponse(
        agent_id=agent.id,
        name=agent.name,
        config=agent.config,
        memory_config=agent.memory.config,
        conversation_history_length=len(agent.conversation_history)
    )

async def update_agent(agent_id: UUID, update_data: Dict[str, Any]) -> bool:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.warning(f"No agent found with id: {agent_id} for update")
        return False

    try:
        if 'config' in update_data:
            agent.config = AgentConfig(**update_data['config'])
        if 'memory_config' in update_data:
            agent.memory.config = MemoryConfig(**update_data['memory_config'])
        agent_logger.info(f"Agent {agent.name} (ID: {agent_id}) updated successfully")
        return True
    except Exception as e:
        agent_logger.error(f"Error updating Agent {agent.name} (ID: {agent_id}): {str(e)}")
        return False

async def delete_agent(agent_id: UUID) -> bool:
    if agent_id in agents:
        del agents[agent_id]
        agent_logger.info(f"Agent (ID: {agent_id}) deleted successfully")
        return True
    agent_logger.warning(f"No agent found with id: {agent_id} for deletion")
    return False

async def list_agents() -> List[AgentInfoResponse]:
    return [
        AgentInfoResponse(
            agent_id=agent.id,
            name=agent.name,
            config=agent.config,
            memory_config=agent.memory.config,
            conversation_history_length=len(agent.conversation_history)
        )
        for agent in agents.values()
    ]

async def get_agent_memory_config(agent_id: UUID) -> MemoryConfig:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return agent.config.memory_config

async def process_message(agent_id: UUID, message: str) -> Tuple[str, List[Dict[str, Any]]]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.process_message(message)

async def register_function(function: FunctionDefinition) -> str:
    function_id = str(uuid4())
    registered_functions[function_id] = function
    agent_logger.info(f"Function {function.name} registered with ID: {function_id}")
    return function_id

async def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Any:
    try:
        agent_logger.info(f"Executing function {function_name} for Agent {self.name} (ID: {self.id})")
        get_function = self.get_function_by_name(function_name)
        if not get_function:
            raise ValueError(f"Unknown function: {function_name}")

        func_impl = registered_functions[get_function.id].implementation

        result = await func_impl(**parameters)  # Ensure this is awaited

        agent_logger.info(f"Function {function_name} executed successfully for Agent {self.name} (ID: {self.id})")
        return result
    except Exception as e:
        agent_logger.error(f"Error executing function {function_name} for Agent {self.name} (ID: {self.id}): {str(e)}")
        raise

def get_available_functions(self) -> List[FunctionDefinition]:
    return [registered_functions[func_id] for func_id in self.available_function_ids if func_id in registered_functions]

async def update_function(function_id: str, updated_function: FunctionDefinition) -> None:
    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    registered_functions[function_id] = updated_function
    agent_logger.info(f"Function with ID: {function_id} updated successfully")

    for agent in agents.values():
        if function_id in agent.available_function_ids:
            agent.add_function(function_id)
            agent_logger.info(f"Updated function {updated_function.name} for Agent {agent.name} (ID: {agent.id})")

async def assign_function_to_agent(agent_id: UUID, function_id: str) -> None:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")

    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    agent.add_function(function_id)
    agent_logger.info(f"Function {registered_functions[function_id].name} assigned to Agent {agent.name} (ID: {agent_id})")

async def remove_function_from_agent(agent_id: UUID, function_id: str) -> None:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")

    if function_id not in registered_functions:
        agent_logger.error(f"No function found with id: {function_id}")
        raise ValueError(f"No function found with id: {function_id}")

    agent.remove_function(function_id)
    agent_logger.info(f"Function {registered_functions[function_id].name} removed from Agent {agent.name} (ID: {agent_id})")

```

# app/core/__init__.py

```py

```

# app/utils/logging.py

```py
import logging
from logging.handlers import RotatingFileHandler
import os
from app.config import settings

def setup_logger(name, log_file, level=logging.INFO):
    """Function to set up a logger with file and console handlers."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # File Handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5)  # 10MB per file, keep 5 old versions
    file_handler.setFormatter(formatter)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create loggers
main_logger = setup_logger('main', os.path.join(settings.LOG_DIR, 'main.log'))
agent_logger = setup_logger('agent', os.path.join(settings.LOG_DIR, 'agent.log'))
memory_logger = setup_logger('memory', os.path.join(settings.LOG_DIR, 'memory.log'))
llm_logger = setup_logger('llm', os.path.join(settings.LOG_DIR, 'llm.log'))
function_logger = setup_logger('function', os.path.join(settings.LOG_DIR, 'function.log'))
auth_logger = setup_logger('auth', os.path.join(settings.LOG_DIR, 'auth.log'))

def get_logger(name: str):
    """Function to get or create a logger by name."""
    if name not in logging.Logger.manager.loggerDict:
        return setup_logger(name, os.path.join(settings.LOG_DIR, f"{name}.log"))
    return logging.getLogger(name)

```

# app/utils/auth.py

```py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.config import settings
from app.utils.logging import setup_logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
auth_logger = setup_logger('auth', settings.LOG_DIR + '/auth.log')

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    auth_logger.debug(f"Received API key: {api_key_header}")
    auth_logger.debug(f"Expected API key: {settings.API_KEY}")
    auth_logger.debug(f"API keys match: {api_key_header == settings.API_KEY}")

    if not api_key_header:
        auth_logger.warning("No API key provided")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="No API key provided"
        )

    if api_key_header == settings.API_KEY:
        auth_logger.info("API key validation successful")
        return api_key_header
    else:
        auth_logger.warning(f"API key validation failed. Received: {api_key_header}, Expected: {settings.API_KEY}")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )

def validate_api_key(api_key: str) -> bool:
    is_valid = api_key == settings.API_KEY
    auth_logger.debug(f"Validating API key: {api_key}")
    auth_logger.debug(f"Expected API key: {settings.API_KEY}")
    auth_logger.debug(f"API keys match: {is_valid}")
    if is_valid:
        auth_logger.info("API key validation successful")
    else:
        auth_logger.warning("API key validation failed")
    return is_valid

```

# app/utils/__init__.py

```py

```

# app/api/__init__.py

```py

```

# app/core/memory/vector_memory.py

```py
import asyncio
from typing import Dict, Any, List
from chromadb import PersistentClient
from chromadb.config import Settings as ChromaDBSettings
from app.utils.logging import memory_logger

class VectorMemory:
    def __init__(self, collection_name: str, chroma_db_settings: ChromaDBSettings):
        self.client = PersistentClient(path=chroma_db_settings.persist_directory)
        self.collection = self.client.get_or_create_collection(collection_name)
        memory_logger.info(f"ChromaDB collection initialized: {collection_name}")

    async def add(self, id: str, content: str, metadata: Dict[str, Any] = {}):
        await asyncio.to_thread(self.collection.add,
                                documents=[content],
                                metadatas=[metadata],
                                ids=[id])
        memory_logger.debug(f"Added document to ChromaDB: {id}")

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        results = await asyncio.to_thread(self.collection.query,
                                          query_texts=[query],
                                          n_results=n_results)
        memory_logger.debug(f"Searched ChromaDB: {query}")
        return [{"id": id, "content": doc, "metadata": meta}
                for id, doc, meta in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])]

```

# app/core/memory/redis_memory.py

```py
from uuid import UUID
from typing import List, Dict, Any
from redis import asyncio as aioredis
from app.utils.logging import memory_logger
from app.config import settings as app_settings

class RedisMemory:
    def __init__(self, agent_id: UUID):
        self.agent_id = agent_id
        self.redis = aioredis.from_url(app_settings.redis_url, encoding="utf-8", decode_responses=True)
        memory_logger.info(f"Redis connection established for agent: {agent_id}")

    async def add(self, key: str, value: str, expire: int = 3600):
        full_key = f"agent:{self.agent_id}:{key}"
        await self.redis.set(full_key, value, ex=expire)
        memory_logger.debug(f"Added key to Redis: {full_key}")

    async def get(self, key: str) -> str:
        full_key = f"agent:{self.agent_id}:{key}"
        value = await self.redis.get(full_key)
        memory_logger.debug(f"Retrieved key from Redis: {full_key}")
        return value

    async def delete(self, key: str):
        full_key = f"agent:{self.agent_id}:{key}"
        await self.redis.delete(full_key)
        memory_logger.debug(f"Deleted key from Redis: {full_key}")

    async def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        pattern = f"agent:{self.agent_id}:*"
        keys = await self.redis.keys(pattern)
        recent_memories = []
        for key in keys[-limit:]:
            value = await self.redis.get(key)
            if value:
                recent_memories.append({"content": value})
        return recent_memories

```

# app/core/memory/memory_system.py

```py
from uuid import UUID, uuid4
from typing import Dict, Any, List, Optional
from app.api.models.memory import MemoryType, MemoryEntry, MemoryOperation
from app.api.models.agent import MemoryConfig
from app.utils.logging import memory_logger
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory
from chromadb.config import Settings as ChromaDBSettings
from app.config import settings as app_settings

class MemorySystem:
    def __init__(self, agent_id: UUID, config: MemoryConfig):
        self.agent_id = agent_id
        self.config = config
        self.short_term = RedisMemory(agent_id)
        chroma_db_settings = ChromaDBSettings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=app_settings.chroma_persist_directory
        )
        self.long_term = VectorMemory(f"agent_{agent_id}", chroma_db_settings)
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, content: str, metadata: Dict[str, Any] = {}) -> str:
        try:
            memory_id = str(uuid4())
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.add(memory_id, content)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                await self.long_term.add(memory_id, content, metadata)
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")

            memory_logger.info(f"{memory_type.value} memory added for agent: {self.agent_id}")
            return memory_id
        except Exception as e:
            memory_logger.error(f"Failed to add {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve(self, memory_type: MemoryType, memory_id: str) -> Optional[MemoryEntry]:
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                content = await self.short_term.get(memory_id)
                return MemoryEntry(content=content) if content else None
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                result = await self.long_term.search(f"id:{memory_id}", n_results=1)
                if result:
                    return MemoryEntry(content=result[0]['content'], metadata=result[0]['metadata'])
                return None
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
        except Exception as e:
            memory_logger.error(
                f"Failed to retrieve {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def search(self, memory_type: MemoryType, query: str, limit: int = 5) -> List[MemoryEntry]:
        try:
            if memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                results = await self.long_term.search(query, n_results=limit)
                return [MemoryEntry(content=result['content'], metadata=result['metadata']) for result in results]
            else:
                raise ValueError(f"Search is only supported for long-term memory")
        except Exception as e:
            memory_logger.error(
                f"Failed to search {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def delete(self, memory_type: MemoryType, memory_id: str):
        try:
            if memory_type == MemoryType.SHORT_TERM and self.config.use_redis_cache:
                await self.short_term.delete(memory_id)
            elif memory_type == MemoryType.LONG_TERM and self.config.use_long_term_memory:
                # Implement deletion for long-term memory (ChromaDB doesn't have a direct delete method)
                # This might involve re-indexing or marking as deleted
                pass
            else:
                raise ValueError(f"Invalid memory type or configuration: {memory_type}")
            memory_logger.info(f"{memory_type.value} memory deleted for agent: {self.agent_id}")
        except Exception as e:
            memory_logger.error(
                f"Failed to delete {memory_type.value} memory for agent: {self.agent_id}. Error: {str(e)}")
            raise

    async def retrieve_relevant(self, context: str, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            relevant_memories = []
            if self.config.use_redis_cache:
                # Retrieve recent memories from short-term memory
                recent_memories = await self.short_term.get_recent(limit)
                relevant_memories.extend(recent_memories)

            if self.config.use_long_term_memory:
                # Search long-term memory for relevant entries
                long_term_results = await self.long_term.search(context, n_results=limit)
                relevant_memories.extend(long_term_results)

            # Sort and limit the combined results
            relevant_memories.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            return relevant_memories[:limit]
        except Exception as e:
            memory_logger.error(f"Error retrieving relevant memories for agent {self.agent_id}: {str(e)}")
            raise

# Global dictionary to store active memory systems
memory_systems: Dict[UUID, MemorySystem] = {}

async def get_memory_system(agent_id: UUID, config: MemoryConfig) -> MemorySystem:
    if agent_id not in memory_systems:
        memory_systems[agent_id] = MemorySystem(agent_id, config)
    return memory_systems[agent_id]

async def add_to_memory(agent_id: UUID, memory_type: MemoryType, entry: MemoryEntry, config: MemoryConfig) -> str:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.add(memory_type, entry.content, entry.metadata)

async def retrieve_from_memory(agent_id: UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig) -> Optional[MemoryEntry]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.retrieve(memory_type, memory_id)

async def search_memory(agent_id: UUID, memory_type: MemoryType, query: str, limit: int, config: MemoryConfig) -> List[MemoryEntry]:
    memory_system = await get_memory_system(agent_id, config)
    return await memory_system.search(memory_type, query, limit)

async def delete_from_memory(agent_id: UUID, memory_type: MemoryType, memory_id: str, config: MemoryConfig):
    memory_system = await get_memory_system(agent_id, config)
    await memory_system.delete(memory_type, memory_id)

async def perform_memory_operation(agent_id: UUID, operation: MemoryOperation, memory_type: MemoryType, data: Dict[str, Any], config: MemoryConfig) -> Any:
    memory_system = await get_memory_system(agent_id, config)
    if operation == MemoryOperation.ADD:
        return await memory_system.add(memory_type, data['content'], data.get('metadata', {}))
    elif operation == MemoryOperation.RETRIEVE:
        return await memory_system.retrieve(memory_type, data['memory_id'])
    elif operation == MemoryOperation.SEARCH:
        return await memory_system.search(memory_type, data['query'], data.get('limit', 5))
    elif operation == MemoryOperation.DELETE:
        await memory_system.delete(memory_type, data['memory_id'])
        return {"message": "Memory deleted successfully"}
    else:
        raise ValueError(f"Invalid memory operation: {operation}")

```

# app/core/memory/__init__.py

```py
from .memory_system import MemorySystem, get_memory_system, add_to_memory, retrieve_from_memory, search_memory, delete_from_memory, perform_memory_operation
from .redis_memory import RedisMemory
from .vector_memory import VectorMemory

__all__ = [
    "MemorySystem",
    "RedisMemory",
    "VectorMemory",
    "get_memory_system",
    "add_to_memory",
    "retrieve_from_memory",
    "search_memory",
    "delete_from_memory",
    "perform_memory_operation",
]

```

# app/api/models/message.py

```py
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from uuid import UUID

class MessageRequest(BaseModel):
    """
    Represents a request to send a message to an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to send the message to")
    content: str = Field(..., description="The content of the message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the message")

class FunctionCall(BaseModel):
    """
    Represents a function call made by the agent.
    """
    name: str = Field(..., description="The name of the function to call")
    arguments: Dict[str, Any] = Field(..., description="The arguments for the function call")

class MessageResponse(BaseModel):
    """
    Represents the response from an agent after processing a message.
    """
    agent_id: UUID = Field(..., description="The ID of the agent that processed the message")
    content: str = Field(..., description="The content of the agent's response")
    function_calls: Optional[List[FunctionCall]] = Field(default=None, description="Any function calls the agent wants to make")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the response")

class MessageHistoryRequest(BaseModel):
    """
    Represents a request to retrieve message history for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve history for")
    limit: int = Field(default=10, ge=1, le=100, description="The maximum number of messages to retrieve")
    before: Optional[str] = Field(default=None, description="Retrieve messages before this timestamp")

class MessageHistoryItem(BaseModel):
    """
    Represents a single item in the message history.
    """
    id: str = Field(..., description="Unique identifier for the message")
    timestamp: str = Field(..., description="Timestamp of when the message was sent or received")
    sender: str = Field(..., description="Identifier of the sender (e.g., 'user' or 'agent')")
    content: str = Field(..., description="Content of the message")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the message")

class MessageHistoryResponse(BaseModel):
    """
    Represents the response containing message history for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    messages: List[MessageHistoryItem] = Field(..., description="List of messages in the history")
    has_more: bool = Field(..., description="Indicates if there are more messages that can be retrieved")

```

# app/api/models/memory.py

```py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID
from enum import Enum

class MemoryType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"

class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"
    DELETE = "delete"

class MemoryEntry(BaseModel):
    """
    Represents a single memory entry.
    """
    content: str = Field(..., description="The content of the memory")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata associated with the memory")

class MemoryAddRequest(BaseModel):
    """
    Represents a request to add a memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to add the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    entry: MemoryEntry = Field(..., description="The memory entry to add")

class MemoryAddResponse(BaseModel):
    """
    Represents the response after adding a memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory_id: str = Field(..., description="The unique identifier assigned to the added memory")
    message: str = Field(..., description="A message indicating the result of the operation")

class MemoryRetrieveRequest(BaseModel):
    """
    Represents a request to retrieve a specific memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to retrieve")

class MemoryRetrieveResponse(BaseModel):
    """
    Represents the response containing a retrieved memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    memory: MemoryEntry = Field(..., description="The retrieved memory entry")

class MemorySearchRequest(BaseModel):
    """
    Represents a request to search memories for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to search memories for")
    memory_type: MemoryType = Field(..., description="The type of memory to search (short-term or long-term)")
    query: str = Field(..., description="The search query")
    limit: int = Field(default=10, ge=1, le=100, description="The maximum number of results to return")

class MemorySearchResponse(BaseModel):
    """
    Represents the response containing search results from memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    results: List[MemoryEntry] = Field(..., description="The list of memory entries matching the search query")

class MemoryDeleteRequest(BaseModel):
    """
    Represents a request to delete a specific memory for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to delete the memory for")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    memory_id: str = Field(..., description="The unique identifier of the memory to delete")

class MemoryDeleteResponse(BaseModel):
    """
    Represents the response after deleting a memory.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    message: str = Field(..., description="A message indicating the result of the deletion")

class MemoryOperationRequest(BaseModel):
    """
    Represents a generic memory operation request.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation to perform")
    memory_type: MemoryType = Field(..., description="The type of memory (short-term or long-term)")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Data required for the operation")

class MemoryOperationResponse(BaseModel):
    """
    Represents a generic memory operation response.
    """
    agent_id: UUID = Field(..., description="The ID of the agent")
    operation: MemoryOperation = Field(..., description="The memory operation that was performed")
    result: Any = Field(..., description="The result of the memory operation")
    message: Optional[str] = Field(default=None, description="An optional message about the operation")

```

# app/api/models/function.py

```py
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from uuid import UUID

class FunctionDefinition(BaseModel):
    """
    Represents the definition of a function that can be called by an agent.
    """
    name: str = Field(..., description="The name of the function", example="calculate_sum")
    description: str = Field(..., description="A brief description of what the function does", example="Calculates the sum of two numbers")
    parameters: Dict[str, Any] = Field(..., description="The parameters the function accepts", example={"a": {"type": "number"}, "b": {"type": "number"}})
    return_type: str = Field(..., description="The type of value the function returns", example="number")

    class Config:
        schema_extra = {
            "example": {
                "name": "calculate_sum",
                "description": "Calculates the sum of two numbers",
                "parameters": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "return_type": "number"
            }
        }

class FunctionRegistrationRequest(BaseModel):
    """
    Represents a request to register a new function for use by agents.
    """
    function: FunctionDefinition = Field(..., description="The function to register")

class FunctionRegistrationResponse(BaseModel):
    """
    Represents the response after registering a new function.
    """
    function_id: str = Field(..., description="The unique identifier assigned to the registered function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the registration", example="Function registered successfully")

class FunctionExecutionRequest(BaseModel):
    """
    Represents a request to execute a function by an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent requesting the function execution", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_name: str = Field(..., description="The name of the function to execute", example="calculate_sum")
    parameters: Dict[str, Any] = Field(..., description="The parameters to pass to the function", example={"a": 5, "b": 3})

class FunctionExecutionResponse(BaseModel):
    """
    Represents the response after executing a function.
    """
    agent_id: UUID = Field(..., description="The ID of the agent that requested the function execution", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_name: str = Field(..., description="The name of the function that was executed", example="calculate_sum")
    result: Any = Field(..., description="The result of the function execution", example=8)
    error: Optional[str] = Field(default=None, description="Any error message if the function execution failed")

class AvailableFunctionsRequest(BaseModel):
    """
    Represents a request to retrieve available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to retrieve available functions for", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")

class AvailableFunctionsResponse(BaseModel):
    """
    Represents the response containing available functions for an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    functions: List[FunctionDefinition] = Field(..., description="List of available functions for the agent")

class FunctionUpdateRequest(BaseModel):
    """
    Represents a request to update an existing function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the function to update", example="func_01234567")
    updated_function: FunctionDefinition = Field(..., description="The updated function definition")

class FunctionUpdateResponse(BaseModel):
    """
    Represents the response after updating a function definition.
    """
    function_id: str = Field(..., description="The unique identifier of the updated function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the update", example="Function updated successfully")

class FunctionAssignmentRequest(BaseModel):
    """
    Represents a request to assign a function to an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent to assign the function to", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_id: str = Field(..., description="The ID of the function to assign", example="func_01234567")

class FunctionAssignmentResponse(BaseModel):
    """
    Represents the response after assigning or removing a function to/from an agent.
    """
    agent_id: UUID = Field(..., description="The ID of the agent", example="3fa85f64-5717-4562-b3fc-2c963f66afa6")
    function_id: str = Field(..., description="The ID of the function", example="func_01234567")
    message: str = Field(..., description="A message indicating the result of the operation", example="Function assigned successfully")

```

# app/api/models/agent.py

```py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from enum import Enum

class MemoryConfig(BaseModel):
    use_long_term_memory: bool = Field(..., description="Whether to use long-term memory storage for the agent")
    use_redis_cache: bool = Field(..., description="Whether to use Redis for short-term memory caching")

class AgentConfig(BaseModel):
    llm_provider: str = Field(..., description="The LLM provider to use for this agent (e.g., 'openai', 'anthropic', 'huggingface')")
    model_name: str = Field(..., description="The specific model name to use (e.g., 'gpt-4', 'claude-v1')")
    temperature: float = Field(..., ge=0.0, le=1.0, description="The temperature setting for the LLM, controlling randomness in outputs")
    max_tokens: int = Field(..., gt=0, description="The maximum number of tokens the LLM should generate in a single response")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")

    model_config = ConfigDict(protected_namespaces=())

class AgentCreationRequest(BaseModel):
    agent_name: str = Field(..., description="The name of the agent to be created")
    agent_config: AgentConfig = Field(..., description="Configuration settings for the agent's language model")
    memory_config: MemoryConfig = Field(..., description="Configuration settings for the agent's memory systems")
    initial_prompt: str = Field(..., description="The initial prompt or instructions to provide to the agent upon creation")

class AgentCreationResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier assigned to the newly created agent")
    message: str = Field(..., description="A message indicating the result of the agent creation process")

class AgentMessageRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to send the message to")
    message: str = Field(..., description="The message content to send to the agent")

class AgentMessageResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent that processed the message")
    response: str = Field(..., description="The agent's response to the input message")
    function_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Any function calls the agent wants to make in response to the message")

class AgentFunctionRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to execute the function for")
    function_name: str = Field(..., description="The name of the function to be executed")
    parameters: Dict[str, Any] = Field(..., description="The parameters to be passed to the function")

class AgentFunctionResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent that executed the function")
    result: Any = Field(..., description="The result returned by the executed function")

class MemoryOperation(str, Enum):
    ADD = "add"
    RETRIEVE = "retrieve"
    SEARCH = "search"

class AgentMemoryRequest(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent to perform the memory operation for")
    operation: MemoryOperation = Field(..., description="The type of memory operation to perform")
    data: Optional[Dict[str, Any]] = Field(None, description="The data to be added or retrieved in memory operations")
    query: Optional[str] = Field(None, description="The search query for memory search operations")

class AgentMemoryResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent the memory operation was performed for")
    result: Any = Field(..., description="The result of the memory operation")

class AgentInfoResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the agent")
    name: str = Field(..., description="The name of the agent")
    config: AgentConfig = Field(..., description="The current configuration of the agent's language model")
    memory_config: MemoryConfig = Field(..., description="The current configuration of the agent's memory systems")
    conversation_history_length: int = Field(..., description="The number of messages in the agent's conversation history")

class AgentUpdateRequest(BaseModel):
    agent_config: Optional[AgentConfig] = Field(None, description="Updated configuration for the agent's language model")
    memory_config: Optional[MemoryConfig] = Field(None, description="Updated configuration for the agent's memory systems")

class AgentUpdateResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the updated agent")
    message: str = Field(..., description="A message indicating the result of the agent update process")

class AgentDeleteResponse(BaseModel):
    agent_id: UUID = Field(..., description="The unique identifier of the deleted agent")
    message: str = Field(..., description="A message indicating the result of the agent deletion process")

```

# app/api/models/__init__.py

```py

```

# app/api/endpoints/message.py

```py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.api.models.agent import AgentMessageRequest, AgentMessageResponse
from app.core.agent import process_message
from app.utils.auth import get_api_key
from app.utils.logging import agent_logger

router = APIRouter()

@router.post("/send", response_model=AgentMessageResponse)
async def send_message_to_agent(request: AgentMessageRequest, api_key: str = Depends(get_api_key)):
    try:
        agent_logger.info(f"Received message for agent: {request.agent_id}")
        response, function_calls = await process_message(request.agent_id, request.message)
        agent_logger.info(f"Successfully processed message for agent: {request.agent_id}")
        return AgentMessageResponse(
            agent_id=request.agent_id,
            response=response,
            function_calls=function_calls
        )
    except ValueError as ve:
        agent_logger.error(f"Agent not found: {request.agent_id}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        agent_logger.error(f"Error processing message for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the message")

# Note: If we want to add an endpoint for retrieving message history, we would add it here.
# This would require implementing a function in app/core/agent.py to retrieve the conversation history.

# @router.get("/{agent_id}/history", response_model=List[MessageHistoryItem])
# async def get_message_history(agent_id: UUID, limit: int = 10, api_key: str = Depends(get_api_key)):
#     # Implementation for retrieving message history
#     pass

```

# app/api/endpoints/memory.py

```py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.memory import (
    MemoryType,
    MemoryEntry,
    MemoryAddRequest,
    MemoryAddResponse,
    MemoryRetrieveRequest,
    MemoryRetrieveResponse,
    MemorySearchRequest,
    MemorySearchResponse,
    MemoryDeleteRequest,
    MemoryDeleteResponse,
    MemoryOperationRequest,
    MemoryOperationResponse
)
from app.core.memory import (
    add_to_memory,
    retrieve_from_memory,
    search_memory,
    delete_from_memory,
    perform_memory_operation
)
from app.core.agent import get_agent_memory_config  # Assuming this function exists to get MemoryConfig for an agent
from app.utils.auth import get_api_key
from app.utils.logging import memory_logger

router = APIRouter()

@router.post("/add", response_model=MemoryAddResponse, status_code=201, summary="Add a memory entry")
async def add_memory_endpoint(
    request: MemoryAddRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Add a new memory entry for an agent.

    - **agent_id**: The ID of the agent to add the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **entry**: The memory entry to add
    """
    try:
        agent_id = UUID(request.agent_id)
        memory_logger.info(f"Adding memory for agent: {agent_id}")
        memory_config = await get_agent_memory_config(agent_id)
        memory_id = await add_to_memory(agent_id, request.memory_type, request.entry, memory_config)
        memory_logger.info(f"Memory added successfully for agent: {agent_id}")
        return MemoryAddResponse(
            agent_id=agent_id,
            memory_id=memory_id,
            message="Memory added successfully"
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        memory_logger.error(f"Error adding memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/retrieve", response_model=MemoryRetrieveResponse, summary="Retrieve a memory entry")
async def retrieve_memory_endpoint(
    request: MemoryRetrieveRequest = Depends(),
    api_key: str = Depends(get_api_key)
):
    """
    Retrieve a specific memory entry for an agent.

    - **agent_id**: The ID of the agent to retrieve the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **memory_id**: The unique identifier of the memory to retrieve
    """
    try:
        memory_logger.info(f"Retrieving memory for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        memory = await retrieve_from_memory(request.agent_id, request.memory_type, request.memory_id, memory_config)
        if memory is None:
            raise HTTPException(status_code=404, detail="Memory not found")
        memory_logger.info(f"Memory retrieved successfully for agent: {request.agent_id}")
        return MemoryRetrieveResponse(
            agent_id=request.agent_id,
            memory=memory
        )
    except HTTPException:
        raise
    except Exception as e:
        memory_logger.error(f"Error retrieving memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=MemorySearchResponse, summary="Search memory entries")
async def search_memory_endpoint(
    request: MemorySearchRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Search memory entries for an agent.

    - **agent_id**: The ID of the agent to search memories for
    - **memory_type**: The type of memory to search (short-term or long-term)
    - **query**: The search query
    - **limit**: The maximum number of results to return
    """
    try:
        memory_logger.info(f"Searching memories for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        results = await search_memory(request.agent_id, request.memory_type, request.query, request.limit, memory_config)
        memory_logger.info(f"Memory search completed for agent: {request.agent_id}")
        return MemorySearchResponse(
            agent_id=request.agent_id,
            results=results
        )
    except Exception as e:
        memory_logger.error(f"Error searching memories for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete", response_model=MemoryDeleteResponse, summary="Delete a memory entry")
async def delete_memory_endpoint(
    request: MemoryDeleteRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Delete a specific memory entry for an agent.

    - **agent_id**: The ID of the agent to delete the memory for
    - **memory_type**: The type of memory (short-term or long-term)
    - **memory_id**: The unique identifier of the memory to delete
    """
    try:
        memory_logger.info(f"Deleting memory for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        await delete_from_memory(request.agent_id, request.memory_type, request.memory_id, memory_config)
        memory_logger.info(f"Memory deleted successfully for agent: {request.agent_id}")
        return MemoryDeleteResponse(
            agent_id=request.agent_id,
            message="Memory deleted successfully"
        )
    except Exception as e:
        memory_logger.error(f"Error deleting memory for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/operate", response_model=MemoryOperationResponse, summary="Perform a memory operation")
async def memory_operation_endpoint(
    request: MemoryOperationRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Perform a generic memory operation for an agent.

    - **agent_id**: The ID of the agent
    - **operation**: The memory operation to perform
    - **memory_type**: The type of memory (short-term or long-term)
    - **data**: Data required for the operation
    """
    try:
        memory_logger.info(f"Performing {request.operation} operation for agent: {request.agent_id}")
        memory_config = await get_agent_memory_config(request.agent_id)
        result = await perform_memory_operation(request.agent_id, request.operation, request.memory_type, request.data, memory_config)
        memory_logger.info(f"{request.operation} operation completed for agent: {request.agent_id}")
        return MemoryOperationResponse(
            agent_id=request.agent_id,
            operation=request.operation,
            result=result,
            message=f"{request.operation} operation completed successfully"
        )
    except Exception as e:
        memory_logger.error(f"Error performing {request.operation} operation for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

```

# app/api/endpoints/function.py

```py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.function import (
    FunctionExecutionRequest,
    FunctionExecutionResponse,
    AvailableFunctionsRequest,
    AvailableFunctionsResponse,
    FunctionDefinition,
    FunctionRegistrationRequest,
    FunctionRegistrationResponse,
    FunctionUpdateRequest,
    FunctionUpdateResponse,
    FunctionAssignmentRequest,
    FunctionAssignmentResponse
)
from app.core.agent import (
    execute_function,
    get_available_functions,
    register_function,
    update_function,
    assign_function_to_agent,
    remove_function_from_agent
)
from app.utils.auth import get_api_key
from app.utils.logging import function_logger

router = APIRouter()

@router.post("/execute", response_model=FunctionExecutionResponse, summary="Execute a function")
async def execute_function_endpoint(
    request: FunctionExecutionRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Execute a function for a specific agent.

    - **agent_id**: The ID of the agent requesting the function execution
    - **function_name**: The name of the function to execute
    - **parameters**: The parameters to pass to the function
    """
    try:
        function_logger.info(f"Executing function {request.function_name} for agent: {request.agent_id}")
        result = await execute_function(request.agent_id, request.function_name, request.parameters)
        function_logger.info(f"Function {request.function_name} executed successfully for agent: {request.agent_id}")
        return FunctionExecutionResponse(
            agent_id=request.agent_id,
            function_name=request.function_name,
            result=result
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function execution: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error executing function {request.function_name} for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while executing the function")

@router.get("/available", response_model=AvailableFunctionsResponse, summary="Get available functions")
async def get_available_functions_endpoint(
    request: AvailableFunctionsRequest = Depends(),
    api_key: str = Depends(get_api_key)
):
    """
    Retrieve available functions for a specific agent.

    - **agent_id**: The ID of the agent to retrieve available functions for
    """
    try:
        function_logger.info(f"Retrieving available functions for agent: {request.agent_id}")
        functions = await get_available_functions(request.agent_id)
        function_logger.info(f"Successfully retrieved available functions for agent: {request.agent_id}")
        return AvailableFunctionsResponse(
            agent_id=request.agent_id,
            functions=functions
        )
    except ValueError as ve:
        function_logger.error(f"Value error in retrieving available functions: {str(ve)}")
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error retrieving available functions for agent {request.agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving available functions")

@router.post("/register", response_model=FunctionRegistrationResponse, status_code=201, summary="Register a new function")
async def register_function_endpoint(
    request: FunctionRegistrationRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Register a new function for use by agents.

    - **function**: The function definition to register
    """
    try:
        function_logger.info(f"Registering new function: {request.function.name}")
        function_id = await register_function(request.function)
        function_logger.info(f"Successfully registered function: {function_id}")
        return FunctionRegistrationResponse(
            function_id=function_id,
            message="Function registered successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function registration: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error registering function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while registering the function")

@router.put("/update", response_model=FunctionUpdateResponse, summary="Update an existing function")
async def update_function_endpoint(
    request: FunctionUpdateRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Update an existing function definition.

    - **function_id**: The unique identifier of the function to update
    - **updated_function**: The updated function definition
    """
    try:
        function_logger.info(f"Updating function: {request.function_id}")
        await update_function(request.function_id, request.updated_function)
        function_logger.info(f"Successfully updated function: {request.function_id}")
        return FunctionUpdateResponse(
            function_id=request.function_id,
            message="Function updated successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function update: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error updating function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the function")

@router.post("/assign", response_model=FunctionAssignmentResponse, summary="Assign a function to an agent")
async def assign_function_endpoint(
    request: FunctionAssignmentRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Assign a function to a specific agent.

    - **agent_id**: The ID of the agent to assign the function to
    - **function_id**: The ID of the function to assign
    """
    try:
        function_logger.info(f"Assigning function {request.function_id} to agent: {request.agent_id}")
        await assign_function_to_agent(request.agent_id, request.function_id)
        function_logger.info(f"Successfully assigned function {request.function_id} to agent: {request.agent_id}")
        return FunctionAssignmentResponse(
            agent_id=request.agent_id,
            function_id=request.function_id,
            message="Function assigned successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function assignment: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error assigning function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while assigning the function")

@router.delete("/remove", response_model=FunctionAssignmentResponse, summary="Remove a function from an agent")
async def remove_function_endpoint(
    agent_id: UUID,
    function_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Remove a function from a specific agent.

    - **agent_id**: The ID of the agent to remove the function from
    - **function_id**: The ID of the function to remove
    """
    try:
        function_logger.info(f"Removing function {function_id} from agent: {agent_id}")
        await remove_function_from_agent(agent_id, function_id)
        function_logger.info(f"Successfully removed function {function_id} from agent: {agent_id}")
        return FunctionAssignmentResponse(
            agent_id=agent_id,
            function_id=function_id,
            message="Function removed successfully"
        )
    except ValueError as ve:
        function_logger.error(f"Value error in function removal: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        function_logger.error(f"Error removing function: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while removing the function")

```

# app/api/endpoints/agent.py

```py
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from typing import List
from app.api.models.agent import AgentCreationRequest, AgentCreationResponse, AgentInfoResponse, AgentUpdateRequest, AgentUpdateResponse
from app.core.agent import create_agent, get_agent_info, update_agent, delete_agent, list_agents
from app.utils.auth import get_api_key

router = APIRouter()

@router.post("/create", response_model=AgentCreationResponse, status_code=201)
async def create_agent_endpoint(request: AgentCreationRequest, api_key: str = Depends(get_api_key)):
    """
    Create a new agent.

    - **name**: The name of the agent
    - **config**: Configuration for the agent's language model
    - **memory_config**: Configuration for the agent's memory systems
    - **initial_prompt**: The initial prompt to send to the agent upon creation
    """
    agent_id = await create_agent(
        name=request.name,
        config=request.config.dict(),
        memory_config=request.memory_config.dict(),
        initial_prompt=request.initial_prompt
    )
    return AgentCreationResponse(agent_id=agent_id, message="Agent created successfully")

@router.get("/{agent_id}", response_model=AgentInfoResponse)
async def get_agent_info_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Retrieve information about a specific agent.

    - **agent_id**: The unique identifier of the agent
    """
    agent_info = await get_agent_info(agent_id=agent_id)
    if agent_info is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_info

@router.patch("/{agent_id}", response_model=AgentUpdateResponse)
async def update_agent_endpoint(agent_id: UUID, request: AgentUpdateRequest, api_key: str = Depends(get_api_key)):
    """
    Update an existing agent.

    - **agent_id**: The unique identifier of the agent to update
    - **config**: Updated configuration for the agent's language model (optional)
    - **memory_config**: Updated configuration for the agent's memory systems (optional)
    """
    updated = await update_agent(
        agent_id=agent_id,
        update_data=request.dict(exclude_unset=True)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentUpdateResponse(agent_id=agent_id, message="Agent updated successfully")

@router.delete("/{agent_id}", status_code=204)
async def delete_agent_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Delete an agent.

    - **agent_id**: The unique identifier of the agent to delete
    """
    deleted = await delete_agent(agent_id=agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")

@router.get("/", response_model=List[AgentInfoResponse])
async def list_agents_endpoint(api_key: str = Depends(get_api_key)):
    """
    List all agents.
    """
    return await list_agents()

```

# app/api/endpoints/__init__.py

```py
from .agent import router as agent_router
from .message import router as message_router
from .function import router as function_router
from .memory import router as memory_router

__all__ = ["agent_router", "message_router", "function_router", "memory_router"]

```

