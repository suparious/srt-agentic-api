# conftest.py

```py
import os
import pytest
import asyncio
from httpx import AsyncClient
from uuid import UUID
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.config import Settings
from app.api.models.agent import AgentConfig, MemoryConfig, LLMProviderConfig
from app.core.llm_provider import LLMProvider
from app.core.memory.redis_memory import RedisMemory
from app.core.memory.vector_memory import VectorMemory
from app.core.agent import Agent
from dotenv import load_dotenv

# Set the TESTING environment variable
os.environ["TESTING"] = "true"

# Load the test environment variables
load_dotenv('.env.test')

@pytest.fixture(scope="session")
def test_settings():
    return Settings(
        API_KEY=os.getenv('API_KEY', 'your_api_key_here'),
        ALLOWED_ORIGINS=["http://testserver", "http://localhost"],
        REDIS_URL="redis://localhost:6379/15",
        CHROMA_PERSIST_DIRECTORY="./test_chroma_db",
        OPENAI_API_KEY="test_openai_key",
        VLLM_API_BASE="https://artemis.hq.solidrust.net/v1",
        LLAMACPP_API_BASE="http://test-llamacpp-server-endpoint",
        TGI_API_BASE="http://test-tgi-server-endpoint",
        ANTHROPIC_API_KEY="test_anthropic_key",
        TESTING=True
    )

@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def test_app(test_settings):
    app.dependency_overrides[Settings] = lambda: test_settings
    yield app
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def redis_memory(event_loop):
    redis_mem = RedisMemory(UUID('00000000-0000-0000-0000-000000000000'))
    await redis_mem.initialize()
    yield redis_mem
    await redis_mem.close()

@pytest.fixture
async def mock_redis_memory():
    return AsyncMock(spec=RedisMemory)

@pytest.fixture
async def mock_vector_memory():
    return AsyncMock(spec=VectorMemory)

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="module")
def sync_client(test_app):
    return TestClient(test_app)

@pytest.fixture(scope="module")
def auth_headers(test_settings):
    return {"X-API-Key": test_settings.API_KEY}

@pytest.fixture
def mock_llm_provider():
    mock_provider = AsyncMock(spec=LLMProvider)
    mock_provider.generate.return_value = "Mocked LLM response"
    return mock_provider

@pytest.fixture
def mock_function_manager():
    return MagicMock()

@pytest.fixture
def mock_memory_system():
    return AsyncMock()

@pytest.fixture
def test_agent_config():
    return AgentConfig(
        llm_providers=[
            LLMProviderConfig(
                provider_type="mock",
                model_name="mock-model"
            )
        ],
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
    )

@pytest.fixture
async def test_agent(async_client: AsyncClient, auth_headers: dict, redis_memory, mock_llm_provider, test_agent_config):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": test_agent_config.model_dump(),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ).model_dump(),
        "initial_prompt": "You are a helpful assistant."
    }

    # Mock the LLM provider creation
    with pytest.MonkeyPatch().context() as m:
        m.setattr("app.core.agent.create_llm_provider", lambda _: mock_llm_provider)
        response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)

    assert response.status_code == 201
    return response.json()["agent_id"]

@pytest.fixture
def test_agent_instance(test_agent_config, mock_function_manager, mock_memory_system):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    return Agent(agent_id, "Test Agent", test_agent_config, mock_memory_system)

# Add a fixture to clean up Redis after each test
@pytest.fixture(autouse=True)
async def cleanup_redis(redis_memory):
    yield
    async with redis_memory.get_connection() as conn:
        await conn.flushdb()

@pytest.fixture(autouse=True, scope="session")
async def cleanup_after_tests(event_loop):
    yield
    await RedisMemory.cleanup()
    tasks = asyncio.all_tasks(event_loop)
    for task in tasks:
        if not task.done():
            task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await event_loop.shutdown_asyncgens()

```

# __init__.py

```py

```

# README.md

```md
# SolidRusT Agentic API Test Suite

This document provides comprehensive guidance for QA Engineers on running, maintaining, and extending the test suite for the SolidRusT Agentic API.

## Test Structure

The test suite is organized into the following categories:

\`\`\`
tests/
├── unit/
│   ├── core/
│   │   ├── memory/
│   │   │   ├── test_memory_system.py
│   │   │   ├── test_redis_memory.py
│   │   │   └── test_vector_memory.py
│   │   ├── test_agent.py
│   │   └── test_llm_provider.py
│   └── api/
│       ├── test_agent.py
│       ├── test_function.py
│       ├── test_memory.py
│       └── test_message.py
├── integration/
│   └── test_redis_memory_integration.py
├── __init__.py
├── conftest.py
└── README.md
\`\`\`

- `unit/`: Contains unit tests for core components and API endpoints.
- `integration/`: Houses integration tests that involve multiple components or external services.
- `conftest.py`: Defines pytest fixtures used across multiple test files.

## pytest Configuration

The project uses a `pytest.ini` file in the root directory to configure pytest behavior. The current configuration is:

\`\`\`ini
[pytest]
asyncio_mode = auto
env_files = .env.test
\`\`\`

This configuration does the following:

1. `asyncio_mode = auto`: Automatically handles asynchronous tests, allowing pytest to run both synchronous and asynchronous tests without additional markers or configurations.

2. `env_files = .env.test`: Specifies that pytest should load environment variables from the `.env.test` file when running tests. This ensures that tests use the correct configuration and credentials for the test environment.

When running tests, pytest will automatically use this configuration. No additional command-line arguments are needed to enable these features.

### Modifying pytest Configuration

If you need to modify the pytest configuration:

1. Edit the `pytest.ini` file in the project root directory.
2. Add or modify options as needed. Refer to the [pytest documentation](https://docs.pytest.org/en/stable/reference/customize.html) for available options.
3. If you add new options, make sure to document them in this README for other team members.

Remember that changes to `pytest.ini` will affect all test runs, so communicate any significant changes to the development team.

## Running Tests

### Full Test Suite

To run the entire test suite:

\`\`\`bash
pytest
\`\`\`

### Specific Test Categories

Run unit tests only:
\`\`\`bash
pytest tests/unit
\`\`\`

Run integration tests only:
\`\`\`bash
pytest tests/integration
\`\`\`

### Individual Test Files

To run tests in a specific file:
\`\`\`bash
pytest tests/path/to/test_file.py
\`\`\`

Example:
\`\`\`bash
pytest tests/unit/api/test_agent.py
\`\`\`

### Test Selection by Markers

Use pytest markers to run specific types of tests:
\`\`\`bash
pytest -m "integration"
\`\`\`

## Writing and Maintaining Tests

1. Follow the existing directory structure when adding new tests.
2. Use descriptive names for test functions, prefixed with `test_`.
3. Utilize pytest fixtures from `conftest.py` for setup and teardown.
4. Aim for high test coverage, including edge cases and error scenarios.
5. Keep tests independent and idempotent.

## Debugging and Reporting Issues

When encountering test failures or unexpected behavior:

1. Run the failing test(s) with increased verbosity:
   \`\`\`bash
   pytest -vv path/to/failing_test.py
   \`\`\`

2. Use the `--pdb` flag to drop into the debugger on test failures:
   \`\`\`bash
   pytest --pdb path/to/failing_test.py
   \`\`\`

3. Generate a detailed test report:
   \`\`\`bash
   pytest --verbose --capture=no --cov=app --cov-report=term-missing > test_results_detailed.txt
   \`\`\`

4. When reporting issues to the AI developer, include:
   - The full test output
   - The `test_results_detailed.txt` file
   - Python version and environment details
   - Any recent changes to the codebase or dependencies

## Continuous Integration

The test suite is integrated into our CI/CD pipeline. Ensure all tests pass locally before pushing changes.

## Handling Warnings

To manage warnings during test runs:

1. Review and address Pydantic-related warnings by updating models to use `ConfigDict`.
2. For dependency-related warnings, update the `pytest.ini` file:

\`\`\`ini
[pytest]
asyncio_mode = auto
env_files = .env.test
filterwarnings =
    ignore::DeprecationWarning:google._upb._message:
    ignore::pydantic.PydanticDeprecatedSince20
\`\`\`

## Performance Considerations

- Unit tests should be fast and not depend on external services.
- Integration tests may be slower due to external dependencies.
- Use the `--durations=N` flag to identify slow tests:
  \`\`\`bash
  pytest --durations=10
  \`\`\`

## Extending the Test Suite

When adding new features or modifying existing ones:

1. Update or add unit tests in the appropriate `unit/` subdirectory.
2. Create or modify integration tests in the `integration/` directory.
3. Update `conftest.py` if new fixtures are required.
4. Ensure backward compatibility of existing tests unless intentionally breaking changes.

By following these guidelines, QA Engineers can effectively utilize, maintain, and extend the test suite, providing valuable feedback to the AI development team and ensuring the reliability of the SolidRusT Agentic API.

```

# unit/__init__.py

```py

```

# integration/test_redis_memory_integration.py

```py
import pytest
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture
async def redis_memory():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    redis_memory = RedisMemory(agent_id)
    yield redis_memory
    # Clean up after tests
    await redis_memory.redis.flushdb()


@pytest.mark.asyncio
async def test_add_and_retrieve_memory_integration(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)
    assert isinstance(memory_id, str)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry.content == memory_entry.content
    assert retrieved_entry.metadata == memory_entry.metadata
    assert retrieved_entry.context.context_type == memory_entry.context.context_type


@pytest.mark.asyncio
async def test_advanced_search_integration(redis_memory):
    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Test memory content {i}",
            metadata={"index": i, "even": i % 2 == 0},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(days=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    query = AdvancedSearchQuery(
        query="content",
        metadata_filters={"even": True},
        time_range={"start": datetime.now() - timedelta(days=4), "end": datetime.now()},
        max_results=3
    )

    results = await redis_memory.search(query)

    assert len(results) <= 3
    assert all(result["memory_entry"].metadata["even"] for result in results)
    assert all(
        datetime.now() - timedelta(days=4) <= result["memory_entry"].context.timestamp <= datetime.now() for result in
        results)


@pytest.mark.asyncio
async def test_delete_memory_integration(redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory to delete",
        metadata={},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    memory_id = await redis_memory.add(memory_entry)
    await redis_memory.delete(memory_id)

    retrieved_entry = await redis_memory.get(memory_id)
    assert retrieved_entry is None


@pytest.mark.asyncio
async def test_get_recent_memories_integration(redis_memory):
    for i in range(10):
        memory_entry = MemoryEntry(
            content=f"Test memory {i}",
            metadata={},
            context=MemoryContext(context_type="test", timestamp=datetime.now() - timedelta(minutes=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    recent_memories = await redis_memory.get_recent(5)
    assert len(recent_memories) == 5
    assert all(memory["memory_entry"].content.startswith("Test memory") for memory in recent_memories)

    # Check if memories are in reverse chronological order
    timestamps = [memory["timestamp"] for memory in recent_memories]
    assert timestamps == sorted(timestamps, reverse=True)


@pytest.mark.asyncio
async def test_get_memories_older_than_integration(redis_memory):
    now = datetime.now()
    threshold = now - timedelta(hours=2)

    # Add test data
    for i in range(5):
        memory_entry = MemoryEntry(
            content=f"Old memory {i}",
            metadata={"index": i},
            context=MemoryContext(context_type="old_test", timestamp=now - timedelta(hours=i), metadata={})
        )
        await redis_memory.add(memory_entry)

    old_memories = await redis_memory.get_memories_older_than(threshold)

    assert len(old_memories) == 3
    assert all(memory.context.timestamp < threshold for memory in old_memories)

# More integration tests can be added here as needed
```

# integration/test_main.py

```py
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_read_main(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SolidRusT Agentic API"}
```

# integration/__init__.py

```py

```

# unit/core/test_llm_provider.py

```py
import pytest
from unittest.mock import AsyncMock, patch
from app.core.llm_provider import LLMProvider, OpenAIProvider, VLLMProvider, LlamaCppServerProvider, APICallException


@pytest.fixture
def provider_configs():
    return [
        {
            "provider_type": "openai",
            "model_name": "gpt-3.5-turbo",
            "api_key": "test-key"
        },
        {
            "provider_type": "vllm",
            "model_name": "llama-7b",
            "api_base": "http://vllm-server:8000"
        },
        {
            "provider_type": "llamacpp",
            "model_name": "llama-13b",
            "api_base": "http://llamacpp-server:8080"
        }
    ]


@pytest.mark.asyncio
async def test_llm_provider_fallback(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai, \
            patch('app.core.llm_provider.VLLMProvider.generate') as mock_vllm, \
            patch('app.core.llm_provider.LlamaCppServerProvider.generate') as mock_llamacpp:
        mock_openai.side_effect = APICallException("OpenAI failed")
        mock_vllm.side_effect = APICallException("vLLM failed")
        mock_llamacpp.return_value = "LlamaCpp response"

        llm_provider = LLMProvider(provider_configs)
        result = await llm_provider.generate("Test prompt", 0.7, 100)

        assert result == "LlamaCpp response"
        mock_openai.assert_called_once()
        mock_vllm.assert_called_once()
        mock_llamacpp.assert_called_once()


@pytest.mark.asyncio
async def test_llm_provider_all_fail(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai, \
            patch('app.core.llm_provider.VLLMProvider.generate') as mock_vllm, \
            patch('app.core.llm_provider.LlamaCppServerProvider.generate') as mock_llamacpp:
        mock_openai.side_effect = APICallException("OpenAI failed")
        mock_vllm.side_effect = APICallException("vLLM failed")
        mock_llamacpp.side_effect = APICallException("LlamaCpp failed")

        llm_provider = LLMProvider(provider_configs)

        with pytest.raises(APICallException, match="LlamaCpp failed"):
            await llm_provider.generate("Test prompt", 0.7, 100)

        mock_openai.assert_called_once()
        mock_vllm.assert_called_once()
        mock_llamacpp.assert_called_once()


@pytest.mark.asyncio
async def test_llm_provider_first_succeeds(provider_configs):
    with patch('app.core.llm_provider.OpenAIProvider.generate') as mock_openai:
        mock_openai.return_value = "OpenAI response"

        llm_provider = LLMProvider(provider_configs)
        result = await llm_provider.generate("Test prompt", 0.7, 100)

        assert result == "OpenAI response"
        mock_openai.assert_called_once()

```

# unit/core/test_agent.py

```py
import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig
from app.api.models.memory import MemoryType, MemoryEntry, MemoryContext, MemoryOperation
from app.core.function_manager import FunctionManager
from app.core.memory import MemorySystem
import json

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_function_manager():
    return MagicMock(spec=FunctionManager)

@pytest.fixture
def mock_memory_system():
    return AsyncMock(spec=MemorySystem)

@pytest.fixture
def test_agent(mock_function_manager, mock_memory_system):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    memory_config = MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
    config = AgentConfig(
        llm_providers=[{"provider_type": "mock", "model_name": "mock-model"}],
        temperature=0.7,
        max_tokens=100,
        memory_config=memory_config  # Add this line
    )
    agent = Agent(agent_id, "Test Agent", config, mock_function_manager)
    agent.memory = mock_memory_system
    agent.llm_provider = AsyncMock()
    return agent

async def test_advanced_search(test_agent, mock_memory_system):
    # Mock memory system's advanced search method
    mock_memory_system.search.return_value = [
        {"content": "Test memory content 1", "metadata": {"key": "value"}, "relevance_score": 0.8},
        {"content": "Test memory content 2", "metadata": {"key": "value"}, "relevance_score": 0.6}
    ]

    search_params = {
        "query": "Test memory",
        "memory_type": MemoryType.LONG_TERM,
        "context_type": "test_context",
        "time_range": {
            "start": datetime.now() - timedelta(hours=3),
            "end": datetime.now()
        },
        "metadata_filters": {"key": "value"},
        "relevance_threshold": 0.5,
        "max_results": 2
    }

    results = await test_agent.memory.search(search_params)

    assert len(results) == 2
    for result in results:
        assert "Test memory" in result["content"]
        assert result["metadata"]["key"] == "value"
        assert result["relevance_score"] >= 0.5

    mock_memory_system.search.assert_called_once()

async def test_add_memory(test_agent, mock_memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test_context",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    mock_memory_system.add.return_value = "test_memory_id"

    memory_id = await test_agent.memory.add(MemoryType.SHORT_TERM, memory_entry)

    assert memory_id == "test_memory_id"
    mock_memory_system.add.assert_called_once_with(MemoryType.SHORT_TERM, memory_entry)

async def test_retrieve_memory(test_agent, mock_memory_system):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(
            context_type="test_context",
            timestamp=datetime.now(),
            metadata={}
        )
    )

    mock_memory_system.retrieve.return_value = memory_entry

    retrieved_memory = await test_agent.memory.retrieve(MemoryType.SHORT_TERM, "test_memory_id")

    assert retrieved_memory == memory_entry
    mock_memory_system.retrieve.assert_called_once_with(MemoryType.SHORT_TERM, "test_memory_id")

async def test_search_memory(test_agent, mock_memory_system):
    mock_memory_system.search.return_value = [
        {"content": "Test memory content", "metadata": {"key": "value"}, "relevance_score": 0.8}
    ]

    search_results = await test_agent.memory.search({
        "query": "Test memory",
        "memory_type": MemoryType.SHORT_TERM,
        "max_results": 5
    })

    assert len(search_results) == 1
    assert search_results[0]["content"] == "Test memory content"
    assert "relevance_score" in search_results[0]
    mock_memory_system.search.assert_called_once()

async def test_delete_memory(test_agent, mock_memory_system):
    await test_agent.memory.delete(MemoryType.SHORT_TERM, "test_memory_id")
    mock_memory_system.delete.assert_called_once_with(MemoryType.SHORT_TERM, "test_memory_id")

async def test_memory_operation(test_agent, mock_memory_system):
    operation_data = {
        "content": "Test operation memory content",
        "metadata": {"operation": "test"},
        "context": {
            "context_type": "test_operation",
            "timestamp": datetime.now(),
            "metadata": {}
        }
    }

    mock_memory_system.perform_operation.return_value = "Operation result"

    result = await test_agent.memory.perform_operation(MemoryOperation.ADD, MemoryType.SHORT_TERM, operation_data)

    assert result == "Operation result"
    mock_memory_system.perform_operation.assert_called_once_with(MemoryOperation.ADD, MemoryType.SHORT_TERM, operation_data)

async def test_process_message(test_agent, mock_memory_system):
    test_agent.llm_provider.generate.return_value = "Test response"
    mock_memory_system.retrieve_relevant.return_value = []

    response, function_calls = await test_agent.process_message("Test message")

    assert response == "Test response"
    assert isinstance(function_calls, list)
    test_agent.llm_provider.generate.assert_called_once()
    mock_memory_system.add.assert_called_once()

async def test_execute_function(test_agent, mock_function_manager):
    mock_function = AsyncMock()
    mock_function.implementation.return_value = "Function result"
    mock_function_manager.registered_functions = {"func1": mock_function}
    test_agent.available_function_ids = ["func1"]

    result = await test_agent.execute_function("func1", {"param": "value"})

    assert result == "Function result"
    mock_function.implementation.assert_called_once_with(param="value")

def test_get_available_functions(test_agent, mock_function_manager):
    mock_function_manager.registered_functions = {
        "func1": MagicMock(name="Function1"),
        "func2": MagicMock(name="Function2")
    }
    test_agent.available_function_ids = ["func1", "func2"]

    available_functions = test_agent.get_available_functions()

    assert len(available_functions) == 2
    assert available_functions[0].name == "Function1"
    assert available_functions[1].name == "Function2"

def test_add_function(test_agent, mock_function_manager):
    mock_function_manager.registered_functions = {"func1": MagicMock(name="Function1")}

    test_agent.add_function("func1")

    assert "func1" in test_agent.available_function_ids

def test_remove_function(test_agent):
    test_agent.available_function_ids = ["func1", "func2"]

    test_agent.remove_function("func1")

    assert "func1" not in test_agent.available_function_ids
    assert "func2" in test_agent.available_function_ids

def test_get_function_by_name(test_agent, mock_function_manager):
    mock_function = MagicMock(name="Function1")
    mock_function_manager.registered_functions = {"func1": mock_function}
    test_agent.available_function_ids = ["func1"]

    result = test_agent.get_function_by_name("Function1")

    assert result == mock_function

def test_prepare_prompt(test_agent):
    context = [{"content": "Context 1"}, {"content": "Context 2"}]
    test_agent.conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ]

    prompt = test_agent._prepare_prompt(context)

    assert "Context: Context 1" in prompt
    assert "Context: Context 2" in prompt
    assert "user: Hello" in prompt
    assert "assistant: Hi there" in prompt

def test_parse_response(test_agent):
    response = "This is a response. FUNCTION CALL: test_function(param1='value1', param2=42)"

    response_text, function_calls = test_agent._parse_response(response)

    assert response_text == "This is a response."
    assert len(function_calls) == 1
    assert function_calls[0]["name"] == "test_function"
    assert function_calls[0]["arguments"] == {"param1": "value1", "param2": 42}

```

# unit/core/__init__.py

```py

```

# unit/api/test_message.py

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

# unit/api/test_memory.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.memory import MemoryType, MemoryOperation
from datetime import datetime, timedelta
import json

pytestmark = pytest.mark.asyncio


async def test_advanced_search(async_client: AsyncClient, auth_headers, test_agent):
    # First, add some test memories
    for i in range(5):
        memory_data = {
            "agent_id": test_agent,
            "memory_type": "LONG_TERM",
            "entry": {
                "content": f"Test memory content {i}",
                "metadata": {"key": "value" if i % 2 == 0 else "other"},
                "context": {
                    "context_type": "test_context",
                    "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                    "metadata": {}
                }
            }
        }
        response = await async_client.post("/memory/add", json=memory_data, headers=auth_headers)
        assert response.status_code == 201

    # Perform advanced search
    search_params = {
        "query": "Test memory",
        "memory_type": "LONG_TERM",
        "context_type": "test_context",
        "time_range_start": (datetime.now() - timedelta(hours=3)).isoformat(),
        "time_range_end": datetime.now().isoformat(),
        "metadata_filters": json.dumps({"key": "value"}),
        "relevance_threshold": 0.5,
        "max_results": 2
    }

    response = await async_client.post(f"/memory/advanced-search?agent_id={test_agent}", params=search_params,
                                       headers=auth_headers)
    assert response.status_code == 200

    results = response.json()
    assert "agent_id" in results
    assert "results" in results
    assert "relevance_scores" in results
    assert len(results["results"]) <= 2

    for result, score in zip(results["results"], results["relevance_scores"]):
        assert "Test memory" in result["content"]
        assert result["metadata"]["key"] == "value"
        assert score >= 0.5

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

@pytest.mark.asyncio
async def test_send_message_invalid_agent(async_client: AsyncClient, auth_headers):
    invalid_agent_id = "00000000-0000-0000-0000-000000000000"
    message_data = {
        "agent_id": invalid_agent_id,
        "content": "This should fail"
    }
    response = await async_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 404
    assert "detail" in response.json()

```

# unit/api/test_function.py

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

@pytest.mark.asyncio
async def test_get_function(async_client: AsyncClient, auth_headers):
    # First, register a function
    function_data = {
        "function": {
            "name": "test_function",
            "description": "A test function",
            "parameters": {},
            "return_type": "string"
        }
    }
    register_response = await async_client.post("/function/register", json=function_data, headers=auth_headers)
    assert register_response.status_code == 201
    function_id = register_response.json()["function_id"]

    # Now, try to get the function
    response = await async_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "test_function"

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

# unit/api/test_agent.py

```py
import pytest
from httpx import AsyncClient
from uuid import UUID
from app.api.models.agent import AgentConfig, MemoryConfig

pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
async def test_create_agent(async_client: AsyncClient, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
        "agent_config": AgentConfig(
            llm_providers=[{"provider_type": "mock", "model_name": "mock-model"}],
            temperature=0.7,
            max_tokens=150,
            memory_config=MemoryConfig(use_long_term_memory=True, use_redis_cache=True)
        ).dict(),
        "memory_config": MemoryConfig(use_long_term_memory=True, use_redis_cache=True).dict(),
        "initial_prompt": "You are a helpful assistant."
    }
    response = await async_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    assert "agent_id" in response.json()

async def test_get_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["agent_id"] == test_agent
    assert agent["name"] == "Test Agent"
    assert "llm_providers" in agent["config"]
    assert isinstance(agent["config"]["llm_providers"], list)

async def test_update_agent(async_client: AsyncClient, auth_headers, test_agent):
    update_data = {
        "agent_config": {
            "temperature": 0.8,
            "llm_providers": [
                {
                    "provider_type": "openai",
                    "model_name": "gpt-4",
                    "api_key": "new-test-key"
                }
            ]
        }
    }
    response = await async_client.patch(f"/agent/{test_agent}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["message"] == "Agent updated successfully"

    # Verify the update
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    agent = response.json()
    assert agent["config"]["temperature"] == 0.8
    assert agent["config"]["llm_providers"][0]["model_name"] == "gpt-4"

async def test_delete_agent(async_client: AsyncClient, auth_headers, test_agent):
    response = await async_client.delete(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 204

    # Verify the agent is deleted
    response = await async_client.get(f"/agent/{test_agent}", headers=auth_headers)
    assert response.status_code == 404

async def test_list_agents(async_client: AsyncClient, auth_headers, test_agent):
    # Create a second agent to ensure we have at least two
    await test_create_agent(async_client, auth_headers)

    response = await async_client.get("/agent", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) >= 2  # We should have at least the two agents we created
    for agent in agents:
        assert "agent_id" in agent
        assert "name" in agent
        assert "config" in agent
        assert "llm_providers" in agent["config"]

```

# unit/api/__init__.py

```py

```

# unit/core/memory/test_vector_memory.py

```py
import pytest
from uuid import UUID
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock
from app.core.memory.vector_memory import VectorMemory
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType

@pytest.fixture
def mock_chroma_client():
    mock_client = MagicMock()
    mock_collection = AsyncMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    return mock_client

@pytest.fixture
def vector_memory(mock_chroma_client):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    vector_memory = VectorMemory(f"agent_{agent_id}")
    vector_memory.client = mock_chroma_client
    vector_memory.collection = mock_chroma_client.get_or_create_collection.return_value
    return vector_memory

@pytest.mark.asyncio
async def test_add_memory(vector_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    await vector_memory.add(memory_entry)
    vector_memory.collection.add.assert_called_once()
    call_args = vector_memory.collection.add.call_args[1]
    assert len(call_args['documents']) == 1
    assert call_args['documents'][0] == memory_entry.content
    assert 'key' in call_args['metadatas'][0]
    assert call_args['metadatas'][0]['key'] == 'value'

@pytest.mark.asyncio
async def test_advanced_search(vector_memory):
    query = AdvancedSearchQuery(
        query="test query",
        memory_type=MemoryType.LONG_TERM,
        context_type="test_context",
        time_range={
            "start": datetime.now() - timedelta(days=1),
            "end": datetime.now()
        },
        metadata_filters={"key": "value"},
        relevance_threshold=0.5,
        max_results=5
    )

    mock_results = {
        'ids': [['1', '2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[
            {'context_type': 'test_context', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'},
            {'context_type': 'test_context', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'}
        ]],
        'distances': [[0.1, 0.6]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 1  # Only one result should pass the relevance threshold
    assert results[0]['id'] == '1'
    assert isinstance(results[0]['memory_entry'], MemoryEntry)
    assert results[0]['relevance_score'] >= 0.5

    # Verify that the query was constructed correctly
    vector_memory.collection.query.assert_called_once()
    call_args = vector_memory.collection.query.call_args[1]
    assert call_args['query_texts'] == ["test query"]
    assert call_args['n_results'] == 5
    assert call_args['where']['context_type'] == "test_context"
    assert call_args['where']['context_timestamp']['$gte'] == query.time_range['start'].isoformat()
    assert call_args['where']['context_timestamp']['$lte'] == query.time_range['end'].isoformat()
    assert call_args['where']['key'] == "value"

@pytest.mark.asyncio
async def test_advanced_search_with_query(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = {
        'ids': [['1', '2']],
        'documents': [['doc1', 'doc2']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat(), 'key': 'value1'},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat(), 'key': 'value2'}
        ]],
        'distances': [[0.1, 0.2]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2
    assert results[0]['id'] == '1'
    assert results[1]['id'] == '2'
    assert isinstance(results[0]['memory_entry'], MemoryEntry)
    assert isinstance(results[1]['memory_entry'], MemoryEntry)


@pytest.mark.asyncio
async def test_advanced_search_with_filters(vector_memory):
    query = AdvancedSearchQuery(
        query="test query",
        context_type="test_type",
        time_range={"start": datetime.now() - timedelta(days=1), "end": datetime.now()},
        metadata_filters={"key": "value"},
        max_results=5
    )
    mock_results = {
        'ids': [['1']],
        'documents': [['doc1']],
        'metadatas': [[{'context_type': 'test_type', 'context_timestamp': datetime.now().isoformat(), 'key': 'value'}]],
        'distances': [[0.1]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 1
    assert results[0]['memory_entry'].context.context_type == "test_type"
    assert results[0]['memory_entry'].metadata["key"] == "value"


@pytest.mark.asyncio
async def test_advanced_search_with_relevance_threshold(vector_memory):
    query = AdvancedSearchQuery(query="test query", relevance_threshold=0.5, max_results=5)
    mock_results = {
        'ids': [['1', '2', '3']],
        'documents': [['doc1', 'doc2', 'doc3']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()}
        ]],
        'distances': [[0.1, 0.5, 0.9]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2  # Only two results should have relevance score >= 0.5
    assert all(result['relevance_score'] >= 0.5 for result in results)


@pytest.mark.asyncio
async def test_advanced_search_empty_results(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = {'ids': [[]], 'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 0


@pytest.mark.asyncio
async def test_advanced_search_with_max_results(vector_memory):
    query = AdvancedSearchQuery(query="test query", max_results=2)
    mock_results = {
        'ids': [['1', '2', '3']],
        'documents': [['doc1', 'doc2', 'doc3']],
        'metadatas': [[
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()},
            {'context_type': 'test', 'context_timestamp': datetime.now().isoformat()}
        ]],
        'distances': [[0.1, 0.2, 0.3]]
    }
    vector_memory.collection.query.return_value = mock_results

    results = await vector_memory.search(query)

    assert len(results) == 2  # Only two results should be returned due to max_results
    assert results[0]['id'] == '1'
    assert results[1]['id'] == '2'

```

# unit/core/memory/test_redis_memory.py

```py
import pytest
import json
from unittest.mock import AsyncMock
from uuid import UUID
from datetime import datetime, timedelta
from app.core.memory.redis_memory import RedisMemory, RedisMemoryError
from app.api.models.memory import AdvancedSearchQuery, MemoryEntry, MemoryContext, MemoryType


@pytest.fixture
def mock_redis_memory():
    return AsyncMock(spec=RedisMemory)


@pytest.mark.asyncio
async def test_add_memory(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    mock_redis_memory.add.return_value = "test_memory_id"

    memory_id = await mock_redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"
    mock_redis_memory.add.assert_called_once_with(memory_entry)


@pytest.mark.asyncio
async def test_get_memory(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test memory content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_redis_memory.get.return_value = memory_entry

    retrieved_entry = await mock_redis_memory.get("test_memory_id")

    assert retrieved_entry == memory_entry
    mock_redis_memory.get.assert_called_once_with("test_memory_id")


@pytest.mark.asyncio
async def test_delete_memory(mock_redis_memory):
    await mock_redis_memory.delete("test_memory_id")
    mock_redis_memory.delete.assert_called_once_with("test_memory_id")


@pytest.mark.asyncio
async def test_search_basic(mock_redis_memory):
    query = AdvancedSearchQuery(query="test query", max_results=5)
    mock_results = [
        {
            "id": "test_key_1",
            "memory_entry": MemoryEntry(
                content="Test memory content",
                metadata={},
                context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
            ),
            "relevance_score": 0.8
        }
    ]
    mock_redis_memory.search.return_value = mock_results

    results = await mock_redis_memory.search(query)

    assert results == mock_results
    mock_redis_memory.search.assert_called_once_with(query)


@pytest.mark.asyncio
async def test_add_memory_with_retry(mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )

    mock_redis_memory.add.side_effect = [
        RedisMemoryError("Simulated failure"),
        RedisMemoryError("Simulated failure"),
        "test_memory_id"
    ]

    memory_id = await mock_redis_memory.add(memory_entry)

    assert isinstance(memory_id, str)
    assert memory_id == "test_memory_id"
    assert mock_redis_memory.add.call_count == 3

# More unit tests can be added here as needed
```

# unit/core/memory/test_memory_system.py

```py
import pytest
from uuid import UUID
from unittest.mock import AsyncMock, MagicMock
from app.core.memory.memory_system import MemorySystem
from app.api.models.agent import MemoryConfig
from app.api.models.memory import MemoryType, MemoryEntry, AdvancedSearchQuery, MemoryOperation, MemoryContext
from datetime import datetime

@pytest.fixture
def mock_redis_memory():
    mock = AsyncMock()
    mock.add.return_value = "mock_memory_id"
    return mock

@pytest.fixture
def mock_vector_memory():
    return AsyncMock()

@pytest.fixture
def memory_config():
    return MemoryConfig(use_long_term_memory=True, use_redis_cache=True)

@pytest.fixture
def memory_system(mock_redis_memory, mock_vector_memory, memory_config):
    return MemorySystem(
        agent_id=UUID('12345678-1234-5678-1234-567812345678'),
        config=memory_config,
        short_term=mock_redis_memory,
        long_term=mock_vector_memory
    )

@pytest.mark.asyncio
async def test_add_short_term_memory(memory_system, mock_redis_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_redis_memory.add.return_value = "memory_id_1"

    result = await memory_system.add(MemoryType.SHORT_TERM, memory_entry)

    assert result == "memory_id_1"
    mock_redis_memory.add.assert_called_once_with(memory_entry)

@pytest.mark.asyncio
async def test_add_long_term_memory(memory_system, mock_vector_memory):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_vector_memory.add.return_value = "memory_id_2"

    result = await memory_system.add(MemoryType.LONG_TERM, memory_entry)

    assert result == "memory_id_2"
    mock_vector_memory.add.assert_called_once_with(memory_entry)

@pytest.mark.asyncio
async def test_retrieve_short_term_memory(memory_system, mock_redis_memory):
    mock_memory = MemoryEntry(
        content="Retrieved content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_redis_memory.get.return_value = mock_memory

    result = await memory_system.retrieve(MemoryType.SHORT_TERM, "memory_id_1")

    assert result == mock_memory
    mock_redis_memory.get.assert_called_once_with("memory_id_1")

@pytest.mark.asyncio
async def test_retrieve_long_term_memory(memory_system, mock_vector_memory):
    mock_memory = MemoryEntry(
        content="Retrieved content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    mock_vector_memory.search.return_value = [{"memory_entry": mock_memory}]

    result = await memory_system.retrieve(MemoryType.LONG_TERM, "memory_id_2")

    assert result == mock_memory
    mock_vector_memory.search.assert_called_once()

@pytest.mark.asyncio
async def test_search(memory_system, mock_redis_memory, mock_vector_memory):
    query = AdvancedSearchQuery(query="test", max_results=5)
    mock_redis_memory.search.return_value = [{"id": "1", "relevance_score": 0.9}]
    mock_vector_memory.search.return_value = [{"id": "2", "relevance_score": 0.8}]

    results = await memory_system.search(query)

    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"
    mock_redis_memory.search.assert_called_once_with(query)
    mock_vector_memory.search.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_delete_short_term_memory(memory_system, mock_redis_memory):
    await memory_system.delete(MemoryType.SHORT_TERM, "memory_id_1")

    mock_redis_memory.delete.assert_called_once_with("memory_id_1")

@pytest.mark.asyncio
async def test_perform_operation_add(memory_system):
    memory_entry = MemoryEntry(
        content="Test content",
        metadata={"key": "value"},
        context=MemoryContext(context_type="test", timestamp=datetime.now(), metadata={})
    )
    result = await memory_system.perform_operation(MemoryOperation.ADD, MemoryType.SHORT_TERM, memory_entry.model_dump())
    assert isinstance(result, str)
    assert result == "mock_memory_id"

@pytest.mark.asyncio
async def test_retrieve_relevant(memory_system, mock_redis_memory, mock_vector_memory):
    mock_redis_memory.get_recent.return_value = [{"id": "1", "timestamp": datetime.now()}]
    mock_vector_memory.search.return_value = [{"id": "2", "timestamp": datetime.now()}]

    results = await memory_system.retrieve_relevant("test context")

    assert len(results) == 2
    mock_redis_memory.get_recent.assert_called_once()
    mock_vector_memory.search.assert_called_once()

@pytest.mark.asyncio
async def test_advanced_search(memory_system, mock_redis_memory, mock_vector_memory):
    query = AdvancedSearchQuery(query="test", max_results=5)
    mock_redis_memory.search.return_value = [{"id": "1", "relevance_score": 0.9}]
    mock_vector_memory.search.return_value = [{"id": "2", "relevance_score": 0.8}]

    results = await memory_system.advanced_search(query)

    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"
    mock_redis_memory.search.assert_called_once_with(query)
    mock_vector_memory.search.assert_called_once_with(query)

@pytest.mark.asyncio
async def test_close(memory_system, mock_redis_memory):
    await memory_system.close()

    mock_redis_memory.close.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_memory_type(memory_system):
    with pytest.raises(ValueError):
        await memory_system.add("INVALID_TYPE", MagicMock())

@pytest.mark.asyncio
async def test_invalid_operation(memory_system):
    with pytest.raises(ValueError):
        await memory_system.perform_operation("INVALID_OPERATION", MemoryType.SHORT_TERM, {})

```

# unit/core/memory/__init__.py

```py

```

# unit/api/models/test_message_models.py

```py
import pytest
from uuid import UUID
from datetime import datetime
from app.api.models.message import (
    MessageRequest,
    FunctionCall,
    MessageResponse,
    MessageHistoryRequest,
    MessageHistoryItem,
    MessageHistoryResponse
)

def test_message_request():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    message_request = MessageRequest(
        agent_id=agent_id,
        content="Hello, agent!",
        metadata={"key": "value"}
    )
    assert message_request.agent_id == agent_id
    assert message_request.content == "Hello, agent!"
    assert message_request.metadata == {"key": "value"}

def test_function_call():
    function_call = FunctionCall(
        name="test_function",
        arguments={"arg1": 1, "arg2": "test"}
    )
    assert function_call.name == "test_function"
    assert function_call.arguments == {"arg1": 1, "arg2": "test"}

def test_message_response():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    function_call = FunctionCall(name="test_function", arguments={"arg1": 1})
    message_response = MessageResponse(
        agent_id=agent_id,
        content="Response from agent",
        function_calls=[function_call],
        metadata={"response_key": "response_value"}
    )
    assert message_response.agent_id == agent_id
    assert message_response.content == "Response from agent"
    assert len(message_response.function_calls) == 1
    assert message_response.function_calls[0].name == "test_function"
    assert message_response.metadata == {"response_key": "response_value"}

def test_message_history_request():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    history_request = MessageHistoryRequest(
        agent_id=agent_id,
        limit=50,
        before="2023-01-01T00:00:00Z"
    )
    assert history_request.agent_id == agent_id
    assert history_request.limit == 50
    assert history_request.before == "2023-01-01T00:00:00Z"

def test_message_history_item():
    history_item = MessageHistoryItem(
        id="msg123",
        timestamp="2023-01-01T12:00:00Z",
        sender="user",
        content="Test message",
        metadata={"item_key": "item_value"}
    )
    assert history_item.id == "msg123"
    assert history_item.timestamp == "2023-01-01T12:00:00Z"
    assert history_item.sender == "user"
    assert history_item.content == "Test message"
    assert history_item.metadata == {"item_key": "item_value"}

def test_message_history_response():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    history_item = MessageHistoryItem(
        id="msg123",
        timestamp="2023-01-01T12:00:00Z",
        sender="user",
        content="Test message"
    )
    history_response = MessageHistoryResponse(
        agent_id=agent_id,
        messages=[history_item],
        has_more=False
    )
    assert history_response.agent_id == agent_id
    assert len(history_response.messages) == 1
    assert history_response.messages[0].id == "msg123"
    assert history_response.has_more == False

def test_message_request_validation():
    with pytest.raises(ValueError):
        MessageRequest(agent_id="invalid_uuid", content="Test")

def test_message_history_request_validation():
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    with pytest.raises(ValueError):
        MessageHistoryRequest(agent_id=agent_id, limit=101)  # Exceeds max limit

    with pytest.raises(ValueError):
        MessageHistoryRequest(agent_id=agent_id, limit=0)  # Below min limit

```

# unit/api/models/__init__.py

```py

```

# unit/api/endpoints/test_memory.py

```py
import pytest
from app.api.endpoints import memory

def test_memory_router_export():
    assert hasattr(memory, 'router'), "memory module should export 'router'"
    from app.api.endpoints.memory import router as internal_router
    assert memory.router == internal_router, "Exported router should be the same as the internal router"

# Add more tests for the actual endpoints here once we've addressed the router export
```

# unit/api/endpoints/__init__.py

```py

```

