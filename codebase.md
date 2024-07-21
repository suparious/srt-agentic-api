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

# .aidigestignore

```
.env
/.venv/
/__pycache__/
/logs/
/data/

```

# tests/conftest.py

```py
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture(scope="module")
def test_client():
    return TestClient(app)

@pytest.fixture(scope="module")
def auth_headers():
    return {"X-API-Key": settings.API_KEY}

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

# docs/llama-cpp-agent.md

```md

```

# docs/custom-instructions.md

```md
Can you write me a good custom instructions prompt for development of this Python FastAPI srt-agentic-api AI Agentic API. Always write all the source files out in full, and use Claude Artifacts.

\`\`\`plaintext
# Custom Instructions for srt-agentic-api Development

## Project Overview
The `srt-agentic-api` is a Python FastAPI-based API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, including memory management, function execution, and message processing.

## Development Guidelines

### 1. Code Structure
- Maintain the existing project structure:
  \`\`\`
  srt-agentic-api/
  ├── app/
  │   ├── api/
  │   │   ├── endpoints/
  │   │   └── models/
  │   ├── core/
  │   └── utils/
  ├── tests/
  ├── docs/
  └── requirements.txt
  \`\`\`
- Keep related functionality together in modules.
- Use clear, descriptive names for files, classes, and functions.

### 2. Coding Style
- Follow PEP 8 guidelines for Python code style.
- Use type hints for function arguments and return values.
- Write docstrings for all public classes and functions.
- Use meaningful variable names that clearly describe their purpose.

### 3. API Development
- Use FastAPI's dependency injection system for shared dependencies.
- Implement proper error handling and return appropriate HTTP status codes.
- Use Pydantic models for request/response schemas.
- Implement API versioning to allow for future changes without breaking existing clients.

### 4. Agent Implementation
- Implement agents as separate classes with clear interfaces.
- Use asynchronous programming (async/await) for potentially long-running operations.
- Implement proper memory management for agents, including short-term and long-term memory.

### 5. Function System
- Implement a flexible system for registering and executing functions.
- Use dependency injection to provide necessary context to functions.
- Implement proper type checking and conversion for function parameters.

### 6. Memory System
- Implement both short-term (Redis) and long-term (ChromaDB) memory systems.
- Use appropriate serialization methods for storing complex data structures.
- Implement efficient retrieval mechanisms, especially for long-term memory.

### 7. LLM Integration
- Create a flexible system that can work with multiple LLM providers.
- Implement proper error handling and retries for LLM API calls.
- Use environment variables for API keys and other sensitive information.

### 8. Testing
- Write unit tests for all core functionality.
- Implement integration tests for API endpoints.
- Use pytest for running tests.
- Aim for high test coverage (at least 80%).

### 9. Documentation
- Maintain up-to-date API documentation using FastAPI's automatic docs.
- Write clear and concise comments in the code where necessary.
- Keep the README.md file updated with setup instructions and basic usage examples.

### 10. Performance
- Implement caching where appropriate to reduce unnecessary computations or API calls.
- Use asynchronous programming to handle concurrent requests efficiently.
- Monitor and optimize database queries for efficiency.

### 11. Security
- Implement proper authentication and authorization mechanisms.
- Sanitize all user inputs to prevent injection attacks.
- Use HTTPS for all communications in production.
- Implement rate limiting to prevent abuse.

### 12. Scalability
- Design the system to be horizontally scalable.
- Use message queues for handling long-running tasks if necessary.
- Implement proper logging for debugging and monitoring.

### 13. Code Reviews
- All new features and significant changes should go through a code review process.
- Use pull requests for proposing and reviewing changes.
- Ensure all tests pass before merging new code.

### 14. Versioning and Deployment
- Use semantic versioning for the API.
- Maintain a CHANGELOG.md file to document changes between versions.
- Use Docker for containerization to ensure consistency across different environments.

### 15. Continuous Integration/Continuous Deployment (CI/CD)
- Set up CI/CD pipelines for automated testing and deployment.
- Automate version bumping and changelog updates.

Remember to always consider the end-user experience when developing new features or making changes. The API should be intuitive, well-documented, and robust.
\`\`\`

```

# docs/ROADMAP.md

```md
# SolidRusT Agentic API Development Roadmap

## Completed Tasks
1. Set up basic project structure
2. Implemented core agent logic (`app/core/agent.py`)
3. Created API models for agent, message, function, and memory
4. Implemented agent, message, function, and memory endpoints
5. Set up logging utility
6. Implemented basic authentication
7. Created and updated `requirements.txt`
8. Updated `README.md` with setup instructions
9. Implemented memory system with Redis and ChromaDB integration
10. Successfully ran the application with a welcome message
11. Enhanced API documentation using Swagger UI
12. Implemented function registration and management system
13. Added function assignment and removal capabilities for agents
14. Implemented actual function execution logic in the `Agent` class

## Current Phase: API Refinement and Advanced Features

1. **Function System Enhancements**
   - [ ] Implement asynchronous function support
   - [ ] Add more robust type checking and conversion for function parameters
   - [ ] Implement function versioning system
   - [ ] Create a set of built-in functions available to all agents

2. **Agent System Improvements**
   - [ ] Implement agent state persistence
   - [ ] Add support for agent templates or archetypes
   - [ ] Develop a system for inter-agent communication

3. **Memory System Optimization**
   - [ ] Implement more sophisticated memory retrieval algorithms
   - [ ] Add support for hierarchical memory structures
   - [ ] Optimize long-term memory storage and retrieval

4. **LLM Integration Enhancements**
   - [ ] Add support for multiple LLM providers
   - [ ] Implement fallback mechanisms for LLM failures
   - [ ] Develop a system for LLM output parsing and validation

5. **Security and Access Control**
   - [ ] Implement role-based access control for API endpoints
   - [ ] Develop a comprehensive authentication system
   - [ ] Implement rate limiting and usage quotas

6. **Monitoring and Observability**
   - [ ] Set up comprehensive logging and monitoring
   - [ ] Implement performance tracking and analytics
   - [ ] Develop a dashboard for system health and usage statistics

## Next Phase: Scaling and Production Readiness

7. **Scalability Enhancements**
   - [ ] Implement horizontal scaling strategies
   - [ ] Optimize database queries and caching
   - [ ] Develop load balancing mechanisms

8. **Testing and Quality Assurance**
   - [ ] Develop comprehensive unit test suite
   - [ ] Implement integration tests for all major components
   - [ ] Set up continuous integration and deployment pipeline

9. **Documentation and User Guide**
   - [ ] Create detailed API documentation
   - [ ] Develop user guide and tutorials
   - [ ] Create SDK for popular programming languages

10. **Deployment and Operations**
    - [ ] Finalize Dockerfile and docker-compose setup
    - [ ] Prepare deployment scripts for various cloud providers
    - [ ] Implement backup and disaster recovery strategies

## Future Considerations

11. **Advanced AI Features**
    - [ ] Implement multi-agent collaboration systems
    - [ ] Develop advanced reasoning and planning capabilities
    - [ ] Explore integration with other AI technologies (e.g., computer vision, speech recognition)

12. **Ecosystem Development**
    - [ ] Create a marketplace for custom functions and agent templates
    - [ ] Develop tools for visual agent and workflow design
    - [ ] Foster a community of developers and researchers around the platform

13. **Ethical AI and Governance**
    - [ ] Implement safeguards against misuse
    - [ ] Develop transparency and explainability features
    - [ ] Create governance structures for responsible AI development
```

# docs/NOTES.md

```md

## Function registration

Example of how to register a new function.

\`\`\`python
def calculate_sum(a: int, b: int) -> int:
    return a + b

function_def = FunctionDefinition(
    name="calculate_sum",
    description="Calculates the sum of two numbers",
    parameters={"a": {"type": "integer"}, "b": {"type": "integer"}},
    return_type="integer",
    implementation=calculate_sum
)

function_id = await register_function(function_def)
\`\`\`

## Formatting for summary

How to generate the `codebase.md` file.

\`\`\`bash
npx ai-digest
\`\`\`

## Testing LLMProvider

To manually test the provider library:

\`\`\`python
from app.config import settings
from app.core.llm_provider import create_llm_provider

provider_config = {
    "provider_type": "openai",
    "model_name": "gpt-3.5-turbo",
    **settings.LLM_PROVIDER_CONFIGS["openai"]
}

llm_provider = create_llm_provider(provider_config)
\`\`\`

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

```

# app/__init__.py

```py

```

# .pytest_cache/README.md

```md
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

# .pytest_cache/CACHEDIR.TAG

```TAG
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

# .pytest_cache/.gitignore

```
# Created by pytest automatically.
*

```

# .idea/workspace.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="AutoImportSettings">
    <option name="autoReloadType" value="SELECTIVE" />
  </component>
  <component name="ChangeListManager">
    <list default="true" id="2f48750f-9426-4d1f-ba88-7ed8f614f74c" name="Changes" comment="Add a README" />
    <option name="SHOW_DIALOG" value="false" />
    <option name="HIGHLIGHT_CONFLICTS" value="true" />
    <option name="HIGHLIGHT_NON_ACTIVE_CHANGELIST" value="false" />
    <option name="LAST_RESOLUTION" value="IGNORE" />
  </component>
  <component name="Git.Settings">
    <option name="RECENT_GIT_ROOT_PATH" value="$PROJECT_DIR$" />
  </component>
  <component name="ProjectColorInfo"><![CDATA[{
  "associatedIndex": 6
}]]></component>
  <component name="ProjectId" id="2jTudosn1Mmw1POHbegMcMdJIfE" />
  <component name="ProjectViewState">
    <option name="hideEmptyMiddlePackages" value="true" />
    <option name="showLibraryContents" value="true" />
  </component>
  <component name="PropertiesComponent"><![CDATA[{
  "keyToString": {
    "ASKED_SHARE_PROJECT_CONFIGURATION_FILES": "true",
    "RunOnceActivity.ShowReadmeOnStart": "true",
    "SHARE_PROJECT_CONFIGURATION_FILES": "true",
    "SONARLINT_PRECOMMIT_ANALYSIS": "true",
    "git-widget-placeholder": "main",
    "last_opened_file_path": "/Users/suparious/repos/srt-agentic-api",
    "node.js.detected.package.eslint": "true",
    "node.js.detected.package.tslint": "true",
    "node.js.selected.package.eslint": "(autodetect)",
    "node.js.selected.package.tslint": "(autodetect)",
    "nodejs_package_manager_path": "npm",
    "settings.editor.selected.configurable": "com.profiq.codexor.SettingsConfigurable",
    "vue.rearranger.settings.migration": "true"
  }
}]]></component>
  <component name="SharedIndexes">
    <attachedChunks>
      <set>
        <option value="bundled-js-predefined-1d06a55b98c1-0b3e54e931b4-JavaScript-PY-241.17890.14" />
        <option value="bundled-python-sdk-5b207ade9991-7e9c3bbb6e34-com.jetbrains.pycharm.pro.sharedIndexes.bundled-PY-241.17890.14" />
      </set>
    </attachedChunks>
  </component>
  <component name="SpellCheckerSettings" RuntimeDictionaries="0" Folders="0" CustomDictionaries="0" DefaultDictionary="application-level" UseSingleDictionary="true" transferred="true" />
  <component name="TaskManager">
    <task active="true" id="Default" summary="Default task">
      <changelist id="2f48750f-9426-4d1f-ba88-7ed8f614f74c" name="Changes" comment="" />
      <created>1721423478316</created>
      <option name="number" value="Default" />
      <option name="presentableId" value="Default" />
      <updated>1721423478316</updated>
      <workItem from="1721423479759" duration="23091000" />
    </task>
    <task id="LOCAL-00001" summary="Setup project">
      <option name="closed" value="true" />
      <created>1721423992038</created>
      <option name="number" value="00001" />
      <option name="presentableId" value="LOCAL-00001" />
      <option name="project" value="LOCAL" />
      <updated>1721423992039</updated>
    </task>
    <task id="LOCAL-00002" summary="Phase 1 implementation">
      <option name="closed" value="true" />
      <created>1721432390190</created>
      <option name="number" value="00002" />
      <option name="presentableId" value="LOCAL-00002" />
      <option name="project" value="LOCAL" />
      <updated>1721432390190</updated>
    </task>
    <task id="LOCAL-00003" summary="update logging and error messaging">
      <option name="closed" value="true" />
      <created>1721451294855</created>
      <option name="number" value="00003" />
      <option name="presentableId" value="LOCAL-00003" />
      <option name="project" value="LOCAL" />
      <updated>1721451294855</updated>
    </task>
    <task id="LOCAL-00004" summary="Add a README">
      <option name="closed" value="true" />
      <created>1721454528301</created>
      <option name="number" value="00004" />
      <option name="presentableId" value="LOCAL-00004" />
      <option name="project" value="LOCAL" />
      <updated>1721454528301</updated>
    </task>
    <option name="localTasksCounter" value="5" />
    <servers />
  </component>
  <component name="TypeScriptGeneratedFilesManager">
    <option name="version" value="3" />
  </component>
  <component name="VcsManagerConfiguration">
    <MESSAGE value="Setup project" />
    <MESSAGE value="Phase 1 implementation" />
    <MESSAGE value="update logging and error messaging" />
    <MESSAGE value="Add a README" />
    <option name="LAST_COMMIT_MESSAGE" value="Add a README" />
  </component>
</project>
```

# .idea/vcs.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="VcsDirectoryMappings">
    <mapping directory="" vcs="Git" />
  </component>
</project>
```

# .idea/srt-agentic-api.iml

```iml
<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <excludeFolder url="file://$MODULE_DIR$/.venv" />
    </content>
    <orderEntry type="jdk" jdkName="Python 3.12 (srt-agentic-api)" jdkType="Python SDK" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
</module>
```

# .idea/modules.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/.idea/srt-agentic-api.iml" filepath="$PROJECT_DIR$/.idea/srt-agentic-api.iml" />
    </modules>
  </component>
</project>
```

# .idea/misc.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="Black">
    <option name="sdkName" value="Python 3.12 (srt-inference-perf)" />
  </component>
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.12 (srt-agentic-api)" project-jdk-type="Python SDK" />
</project>
```

# .idea/dbnavigator.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="DBNavigator.Project.DatabaseFileManager">
    <open-files />
  </component>
  <component name="DBNavigator.Project.Settings">
    <connections />
    <browser-settings>
      <general>
        <display-mode value="TABBED" />
        <navigation-history-size value="100" />
        <show-object-details value="false" />
        <enable-sticky-paths value="true" />
      </general>
      <filters>
        <object-type-filter>
          <object-type name="SCHEMA" enabled="true" />
          <object-type name="USER" enabled="true" />
          <object-type name="ROLE" enabled="true" />
          <object-type name="PRIVILEGE" enabled="true" />
          <object-type name="CHARSET" enabled="true" />
          <object-type name="TABLE" enabled="true" />
          <object-type name="VIEW" enabled="true" />
          <object-type name="MATERIALIZED_VIEW" enabled="true" />
          <object-type name="NESTED_TABLE" enabled="true" />
          <object-type name="COLUMN" enabled="true" />
          <object-type name="INDEX" enabled="true" />
          <object-type name="CONSTRAINT" enabled="true" />
          <object-type name="DATASET_TRIGGER" enabled="true" />
          <object-type name="DATABASE_TRIGGER" enabled="true" />
          <object-type name="SYNONYM" enabled="true" />
          <object-type name="SEQUENCE" enabled="true" />
          <object-type name="PROCEDURE" enabled="true" />
          <object-type name="FUNCTION" enabled="true" />
          <object-type name="PACKAGE" enabled="true" />
          <object-type name="TYPE" enabled="true" />
          <object-type name="TYPE_ATTRIBUTE" enabled="true" />
          <object-type name="ARGUMENT" enabled="true" />
          <object-type name="DIMENSION" enabled="true" />
          <object-type name="CLUSTER" enabled="true" />
          <object-type name="DBLINK" enabled="true" />
        </object-type-filter>
      </filters>
      <sorting>
        <object-type name="COLUMN" sorting-type="NAME" />
        <object-type name="FUNCTION" sorting-type="NAME" />
        <object-type name="PROCEDURE" sorting-type="NAME" />
        <object-type name="ARGUMENT" sorting-type="POSITION" />
        <object-type name="TYPE ATTRIBUTE" sorting-type="POSITION" />
      </sorting>
      <default-editors>
        <object-type name="VIEW" editor-type="SELECTION" />
        <object-type name="PACKAGE" editor-type="SELECTION" />
        <object-type name="TYPE" editor-type="SELECTION" />
      </default-editors>
    </browser-settings>
    <navigation-settings>
      <lookup-filters>
        <lookup-objects>
          <object-type name="SCHEMA" enabled="true" />
          <object-type name="USER" enabled="false" />
          <object-type name="ROLE" enabled="false" />
          <object-type name="PRIVILEGE" enabled="false" />
          <object-type name="CHARSET" enabled="false" />
          <object-type name="TABLE" enabled="true" />
          <object-type name="VIEW" enabled="true" />
          <object-type name="MATERIALIZED VIEW" enabled="true" />
          <object-type name="INDEX" enabled="true" />
          <object-type name="CONSTRAINT" enabled="true" />
          <object-type name="DATASET TRIGGER" enabled="true" />
          <object-type name="DATABASE TRIGGER" enabled="true" />
          <object-type name="SYNONYM" enabled="false" />
          <object-type name="SEQUENCE" enabled="true" />
          <object-type name="PROCEDURE" enabled="true" />
          <object-type name="FUNCTION" enabled="true" />
          <object-type name="PACKAGE" enabled="true" />
          <object-type name="TYPE" enabled="true" />
          <object-type name="DIMENSION" enabled="false" />
          <object-type name="CLUSTER" enabled="false" />
          <object-type name="DBLINK" enabled="true" />
        </lookup-objects>
        <force-database-load value="false" />
        <prompt-connection-selection value="true" />
        <prompt-schema-selection value="true" />
      </lookup-filters>
    </navigation-settings>
    <dataset-grid-settings>
      <general>
        <enable-zooming value="true" />
        <enable-column-tooltip value="true" />
      </general>
      <sorting>
        <nulls-first value="true" />
        <max-sorting-columns value="4" />
      </sorting>
      <audit-columns>
        <column-names value="" />
        <visible value="true" />
        <editable value="false" />
      </audit-columns>
    </dataset-grid-settings>
    <dataset-editor-settings>
      <text-editor-popup>
        <active value="false" />
        <active-if-empty value="false" />
        <data-length-threshold value="100" />
        <popup-delay value="1000" />
      </text-editor-popup>
      <values-actions-popup>
        <show-popup-button value="true" />
        <element-count-threshold value="1000" />
        <data-length-threshold value="250" />
      </values-actions-popup>
      <general>
        <fetch-block-size value="100" />
        <fetch-timeout value="30" />
        <trim-whitespaces value="true" />
        <convert-empty-strings-to-null value="true" />
        <select-content-on-cell-edit value="true" />
        <large-value-preview-active value="true" />
      </general>
      <filters>
        <prompt-filter-dialog value="true" />
        <default-filter-type value="BASIC" />
      </filters>
      <qualified-text-editor text-length-threshold="300">
        <content-types>
          <content-type name="Text" enabled="true" />
          <content-type name="Properties" enabled="true" />
          <content-type name="XML" enabled="true" />
          <content-type name="DTD" enabled="true" />
          <content-type name="HTML" enabled="true" />
          <content-type name="XHTML" enabled="true" />
          <content-type name="CSS" enabled="true" />
          <content-type name="SQL" enabled="true" />
          <content-type name="PL/SQL" enabled="true" />
          <content-type name="JavaScript" enabled="true" />
          <content-type name="JSON" enabled="true" />
          <content-type name="JSON5" enabled="true" />
          <content-type name="YAML" enabled="true" />
        </content-types>
      </qualified-text-editor>
      <record-navigation>
        <navigation-target value="VIEWER" />
      </record-navigation>
    </dataset-editor-settings>
    <code-editor-settings>
      <general>
        <show-object-navigation-gutter value="false" />
        <show-spec-declaration-navigation-gutter value="true" />
        <enable-spellchecking value="true" />
        <enable-reference-spellchecking value="false" />
      </general>
      <confirmations>
        <save-changes value="false" />
        <revert-changes value="true" />
        <exit-on-changes value="ASK" />
      </confirmations>
    </code-editor-settings>
    <code-completion-settings>
      <filters>
        <basic-filter>
          <filter-element type="RESERVED_WORD" id="keyword" selected="true" />
          <filter-element type="RESERVED_WORD" id="function" selected="true" />
          <filter-element type="RESERVED_WORD" id="parameter" selected="true" />
          <filter-element type="RESERVED_WORD" id="datatype" selected="true" />
          <filter-element type="RESERVED_WORD" id="exception" selected="true" />
          <filter-element type="OBJECT" id="schema" selected="true" />
          <filter-element type="OBJECT" id="role" selected="true" />
          <filter-element type="OBJECT" id="user" selected="true" />
          <filter-element type="OBJECT" id="privilege" selected="true" />
          <user-schema>
            <filter-element type="OBJECT" id="table" selected="true" />
            <filter-element type="OBJECT" id="view" selected="true" />
            <filter-element type="OBJECT" id="materialized view" selected="true" />
            <filter-element type="OBJECT" id="index" selected="true" />
            <filter-element type="OBJECT" id="constraint" selected="true" />
            <filter-element type="OBJECT" id="trigger" selected="true" />
            <filter-element type="OBJECT" id="synonym" selected="false" />
            <filter-element type="OBJECT" id="sequence" selected="true" />
            <filter-element type="OBJECT" id="procedure" selected="true" />
            <filter-element type="OBJECT" id="function" selected="true" />
            <filter-element type="OBJECT" id="package" selected="true" />
            <filter-element type="OBJECT" id="type" selected="true" />
            <filter-element type="OBJECT" id="dimension" selected="true" />
            <filter-element type="OBJECT" id="cluster" selected="true" />
            <filter-element type="OBJECT" id="dblink" selected="true" />
          </user-schema>
          <public-schema>
            <filter-element type="OBJECT" id="table" selected="false" />
            <filter-element type="OBJECT" id="view" selected="false" />
            <filter-element type="OBJECT" id="materialized view" selected="false" />
            <filter-element type="OBJECT" id="index" selected="false" />
            <filter-element type="OBJECT" id="constraint" selected="false" />
            <filter-element type="OBJECT" id="trigger" selected="false" />
            <filter-element type="OBJECT" id="synonym" selected="false" />
            <filter-element type="OBJECT" id="sequence" selected="false" />
            <filter-element type="OBJECT" id="procedure" selected="false" />
            <filter-element type="OBJECT" id="function" selected="false" />
            <filter-element type="OBJECT" id="package" selected="false" />
            <filter-element type="OBJECT" id="type" selected="false" />
            <filter-element type="OBJECT" id="dimension" selected="false" />
            <filter-element type="OBJECT" id="cluster" selected="false" />
            <filter-element type="OBJECT" id="dblink" selected="false" />
          </public-schema>
          <any-schema>
            <filter-element type="OBJECT" id="table" selected="true" />
            <filter-element type="OBJECT" id="view" selected="true" />
            <filter-element type="OBJECT" id="materialized view" selected="true" />
            <filter-element type="OBJECT" id="index" selected="true" />
            <filter-element type="OBJECT" id="constraint" selected="true" />
            <filter-element type="OBJECT" id="trigger" selected="true" />
            <filter-element type="OBJECT" id="synonym" selected="true" />
            <filter-element type="OBJECT" id="sequence" selected="true" />
            <filter-element type="OBJECT" id="procedure" selected="true" />
            <filter-element type="OBJECT" id="function" selected="true" />
            <filter-element type="OBJECT" id="package" selected="true" />
            <filter-element type="OBJECT" id="type" selected="true" />
            <filter-element type="OBJECT" id="dimension" selected="true" />
            <filter-element type="OBJECT" id="cluster" selected="true" />
            <filter-element type="OBJECT" id="dblink" selected="true" />
          </any-schema>
        </basic-filter>
        <extended-filter>
          <filter-element type="RESERVED_WORD" id="keyword" selected="true" />
          <filter-element type="RESERVED_WORD" id="function" selected="true" />
          <filter-element type="RESERVED_WORD" id="parameter" selected="true" />
          <filter-element type="RESERVED_WORD" id="datatype" selected="true" />
          <filter-element type="RESERVED_WORD" id="exception" selected="true" />
          <filter-element type="OBJECT" id="schema" selected="true" />
          <filter-element type="OBJECT" id="user" selected="true" />
          <filter-element type="OBJECT" id="role" selected="true" />
          <filter-element type="OBJECT" id="privilege" selected="true" />
          <user-schema>
            <filter-element type="OBJECT" id="table" selected="true" />
            <filter-element type="OBJECT" id="view" selected="true" />
            <filter-element type="OBJECT" id="materialized view" selected="true" />
            <filter-element type="OBJECT" id="index" selected="true" />
            <filter-element type="OBJECT" id="constraint" selected="true" />
            <filter-element type="OBJECT" id="trigger" selected="true" />
            <filter-element type="OBJECT" id="synonym" selected="true" />
            <filter-element type="OBJECT" id="sequence" selected="true" />
            <filter-element type="OBJECT" id="procedure" selected="true" />
            <filter-element type="OBJECT" id="function" selected="true" />
            <filter-element type="OBJECT" id="package" selected="true" />
            <filter-element type="OBJECT" id="type" selected="true" />
            <filter-element type="OBJECT" id="dimension" selected="true" />
            <filter-element type="OBJECT" id="cluster" selected="true" />
            <filter-element type="OBJECT" id="dblink" selected="true" />
          </user-schema>
          <public-schema>
            <filter-element type="OBJECT" id="table" selected="true" />
            <filter-element type="OBJECT" id="view" selected="true" />
            <filter-element type="OBJECT" id="materialized view" selected="true" />
            <filter-element type="OBJECT" id="index" selected="true" />
            <filter-element type="OBJECT" id="constraint" selected="true" />
            <filter-element type="OBJECT" id="trigger" selected="true" />
            <filter-element type="OBJECT" id="synonym" selected="true" />
            <filter-element type="OBJECT" id="sequence" selected="true" />
            <filter-element type="OBJECT" id="procedure" selected="true" />
            <filter-element type="OBJECT" id="function" selected="true" />
            <filter-element type="OBJECT" id="package" selected="true" />
            <filter-element type="OBJECT" id="type" selected="true" />
            <filter-element type="OBJECT" id="dimension" selected="true" />
            <filter-element type="OBJECT" id="cluster" selected="true" />
            <filter-element type="OBJECT" id="dblink" selected="true" />
          </public-schema>
          <any-schema>
            <filter-element type="OBJECT" id="table" selected="true" />
            <filter-element type="OBJECT" id="view" selected="true" />
            <filter-element type="OBJECT" id="materialized view" selected="true" />
            <filter-element type="OBJECT" id="index" selected="true" />
            <filter-element type="OBJECT" id="constraint" selected="true" />
            <filter-element type="OBJECT" id="trigger" selected="true" />
            <filter-element type="OBJECT" id="synonym" selected="true" />
            <filter-element type="OBJECT" id="sequence" selected="true" />
            <filter-element type="OBJECT" id="procedure" selected="true" />
            <filter-element type="OBJECT" id="function" selected="true" />
            <filter-element type="OBJECT" id="package" selected="true" />
            <filter-element type="OBJECT" id="type" selected="true" />
            <filter-element type="OBJECT" id="dimension" selected="true" />
            <filter-element type="OBJECT" id="cluster" selected="true" />
            <filter-element type="OBJECT" id="dblink" selected="true" />
          </any-schema>
        </extended-filter>
      </filters>
      <sorting enabled="true">
        <sorting-element type="RESERVED_WORD" id="keyword" />
        <sorting-element type="RESERVED_WORD" id="datatype" />
        <sorting-element type="OBJECT" id="column" />
        <sorting-element type="OBJECT" id="table" />
        <sorting-element type="OBJECT" id="view" />
        <sorting-element type="OBJECT" id="materialized view" />
        <sorting-element type="OBJECT" id="index" />
        <sorting-element type="OBJECT" id="constraint" />
        <sorting-element type="OBJECT" id="trigger" />
        <sorting-element type="OBJECT" id="synonym" />
        <sorting-element type="OBJECT" id="sequence" />
        <sorting-element type="OBJECT" id="procedure" />
        <sorting-element type="OBJECT" id="function" />
        <sorting-element type="OBJECT" id="package" />
        <sorting-element type="OBJECT" id="type" />
        <sorting-element type="OBJECT" id="dimension" />
        <sorting-element type="OBJECT" id="cluster" />
        <sorting-element type="OBJECT" id="dblink" />
        <sorting-element type="OBJECT" id="schema" />
        <sorting-element type="OBJECT" id="role" />
        <sorting-element type="OBJECT" id="user" />
        <sorting-element type="RESERVED_WORD" id="function" />
        <sorting-element type="RESERVED_WORD" id="parameter" />
      </sorting>
      <format>
        <enforce-code-style-case value="true" />
      </format>
    </code-completion-settings>
    <execution-engine-settings>
      <statement-execution>
        <fetch-block-size value="100" />
        <execution-timeout value="20" />
        <debug-execution-timeout value="600" />
        <focus-result value="false" />
        <prompt-execution value="false" />
      </statement-execution>
      <script-execution>
        <command-line-interfaces />
        <execution-timeout value="300" />
      </script-execution>
      <method-execution>
        <execution-timeout value="30" />
        <debug-execution-timeout value="600" />
        <parameter-history-size value="10" />
      </method-execution>
    </execution-engine-settings>
    <operation-settings>
      <transactions>
        <uncommitted-changes>
          <on-project-close value="ASK" />
          <on-disconnect value="ASK" />
          <on-autocommit-toggle value="ASK" />
        </uncommitted-changes>
        <multiple-uncommitted-changes>
          <on-commit value="ASK" />
          <on-rollback value="ASK" />
        </multiple-uncommitted-changes>
      </transactions>
      <session-browser>
        <disconnect-session value="ASK" />
        <kill-session value="ASK" />
        <reload-on-filter-change value="false" />
      </session-browser>
      <compiler>
        <compile-type value="KEEP" />
        <compile-dependencies value="ASK" />
        <always-show-controls value="false" />
      </compiler>
    </operation-settings>
    <ddl-file-settings>
      <extensions>
        <mapping file-type-id="VIEW" extensions="vw" />
        <mapping file-type-id="TRIGGER" extensions="trg" />
        <mapping file-type-id="PROCEDURE" extensions="prc" />
        <mapping file-type-id="FUNCTION" extensions="fnc" />
        <mapping file-type-id="PACKAGE" extensions="pkg" />
        <mapping file-type-id="PACKAGE_SPEC" extensions="pks" />
        <mapping file-type-id="PACKAGE_BODY" extensions="pkb" />
        <mapping file-type-id="TYPE" extensions="tpe" />
        <mapping file-type-id="TYPE_SPEC" extensions="tps" />
        <mapping file-type-id="TYPE_BODY" extensions="tpb" />
      </extensions>
      <general>
        <lookup-ddl-files value="true" />
        <create-ddl-files value="false" />
        <synchronize-ddl-files value="true" />
        <use-qualified-names value="false" />
        <make-scripts-rerunnable value="true" />
      </general>
    </ddl-file-settings>
    <general-settings>
      <regional-settings>
        <date-format value="MEDIUM" />
        <number-format value="UNGROUPED" />
        <locale value="SYSTEM_DEFAULT" />
        <use-custom-formats value="false" />
      </regional-settings>
      <environment>
        <environment-types>
          <environment-type id="development" name="Development" description="Development environment" color="-2430209/-12296320" readonly-code="false" readonly-data="false" />
          <environment-type id="integration" name="Integration" description="Integration environment" color="-2621494/-12163514" readonly-code="true" readonly-data="false" />
          <environment-type id="production" name="Production" description="Productive environment" color="-11574/-10271420" readonly-code="true" readonly-data="true" />
          <environment-type id="other" name="Other" description="" color="-1576/-10724543" readonly-code="false" readonly-data="false" />
        </environment-types>
        <visibility-settings>
          <connection-tabs value="true" />
          <dialog-headers value="true" />
          <object-editor-tabs value="true" />
          <script-editor-tabs value="false" />
          <execution-result-tabs value="true" />
        </visibility-settings>
      </environment>
    </general-settings>
  </component>
</project>
```

# .idea/aws.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="accountSettings">
    <option name="activeProfile" value="profile:default" />
    <option name="activeRegion" value="us-west-2" />
    <option name="recentlyUsedProfiles">
      <list>
        <option value="profile:default" />
      </list>
    </option>
    <option name="recentlyUsedRegions">
      <list>
        <option value="us-west-2" />
      </list>
    </option>
  </component>
</project>
```

# .idea/.gitignore

```
# Default ignored files
/shelf/
/workspace.xml
# Editor-based HTTP Client requests
/httpRequests/
# Datasource local storage ignored files
/dataSources/
/dataSources.local.xml
# Zeppelin ignored files
/ZeppelinRemoteNotebooks/

```

# tests/test_core/test_memory.py

```py

```

# tests/test_core/test_agent.py

```py
import pytest
from unittest.mock import Mock, patch
from uuid import UUID
from app.core.agent import Agent
from app.api.models.agent import AgentConfig, MemoryConfig


@pytest.fixture
def mock_llm_provider():
    return Mock()


@pytest.fixture
def mock_memory_system():
    return Mock()


@pytest.fixture
def agent_config():
    return AgentConfig(
        llm_provider="openai",  # Change this from "test_provider" to "openai"
        model_name="gpt-3.5-turbo",
        temperature=0.7,
        max_tokens=100,
        memory_config=MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        )
    )

@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
@pytest.mark.asyncio
async def test_agent_initialization(mock_llm_provider, mock_memory_system, agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    with patch('app.core.agent.create_llm_provider', return_value=mock_llm_provider):
        agent = Agent(
            agent_id=agent_id,
            name="Test Agent",
            config=agent_config,
            memory_config=agent_config.memory_config
        )

    assert agent.id == agent_id
    assert agent.name == "Test Agent"
    assert agent.config == agent_config
    assert agent.llm_provider == mock_llm_provider

@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
@pytest.mark.asyncio
async def test_agent_process_message(mock_memory_system, mock_create_llm_provider, agent_config):
    mock_llm_provider = Mock()
    mock_create_llm_provider.return_value = mock_llm_provider
    mock_llm_provider.generate.return_value = "Processed message response"

    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    message = "Test message"
    response, function_calls = await agent.process_message(message)

    assert response == "Processed message response"
    assert function_calls == []
    mock_llm_provider.generate.assert_called_once()
    agent.memory.add.assert_called_once()


@patch('app.core.agent.create_llm_provider')
@patch('app.core.agent.MemorySystem')
def test_agent_execute_function(mock_memory_system, mock_create_llm_provider, agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    def test_function(param1, param2):
        return f"Executed with {param1} and {param2}"

    agent.available_function_ids = ["test_function_id"]
    with patch.dict('app.core.agent.registered_functions', {"test_function_id": Mock(implementation=test_function)}):
        result = agent.execute_function("test_function", {"param1": "value1", "param2": "value2"})

    assert result == "Executed with value1 and value2"


def test_agent_get_available_functions(agent_config):
    agent_id = UUID('12345678-1234-5678-1234-567812345678')
    agent = Agent(
        agent_id=agent_id,
        name="Test Agent",
        config=agent_config,
        memory_config=agent_config.memory_config
    )

    agent.available_function_ids = ["function1", "function2"]
    with patch.dict('app.core.agent.registered_functions', {
        "function1": Mock(name="Function 1"),
        "function2": Mock(name="Function 2")
    }):
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
from fastapi.testclient import TestClient
from uuid import UUID
from app.core.agent import create_agent
from httpx import AsyncClient
from app.api.models.agent import AgentConfig, MemoryConfig

@pytest.fixture
async def test_agent(test_client: TestClient, auth_headers):
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
        ),
        "memory_config": MemoryConfig(
            use_long_term_memory=True,
            use_redis_cache=True
        ),
        "initial_prompt": "You are a helpful assistant."
    }
    agent_id = await create_agent(**agent_data)
    return agent_id

@pytest.mark.asyncio
async def test_send_message(test_client: AsyncClient, auth_headers, test_agent):
    agent_id = await test_agent
    message_data = {
        "agent_id": str(agent_id),
        "message": "Hello, agent!"
    }
    response = await test_client.post("/message/send", json=message_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "agent_id" in result
    assert "response" in result
    assert isinstance(result.get("function_calls"), list) or result.get("function_calls") is None
    return result

@pytest.mark.asyncio
async def test_get_message_history(test_client: AsyncClient, auth_headers, test_agent):
    # First, send a message to ensure there's some history
    sent_message = await test_send_message(test_client, auth_headers, test_agent)

    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = await test_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history["messages"], list)
    assert len(history["messages"]) > 0
    assert history["messages"][0]["content"] == "Hello, agent!"


def test_clear_message_history(test_client: TestClient, auth_headers):
    # First, send a message to ensure there's some history
    sent_message = test_send_message(test_client, auth_headers)

    clear_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = test_client.post("/message/clear", json=clear_request, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Message history cleared successfully"

    # Verify that the history is indeed cleared
    history_request = {
        "agent_id": sent_message["agent_id"],
        "limit": 10
    }
    response = test_client.get("/message/history", params=history_request, headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history["messages"]) == 0


def test_get_latest_message(test_client: TestClient, auth_headers):
    # First, send a message
    sent_message = test_send_message(test_client, auth_headers)

    latest_request = {
        "agent_id": sent_message["agent_id"]
    }
    response = test_client.get("/message/latest", params=latest_request, headers=auth_headers)
    assert response.status_code == 200
    latest_message = response.json()
    assert latest_message["content"] == "Hello, agent!"

```

# tests/test_api/test_memory.py

```py
import pytest
from fastapi.testclient import TestClient
from uuid import UUID

def test_add_memory(test_client: TestClient, auth_headers):
    memory_data = {
        "agent_id": str(UUID(int=0)),  # Using a dummy UUID for testing
        "memory_type": "SHORT_TERM",
        "entry": {
            "content": "Test memory content",
            "metadata": {"key": "value"}
        }
    }
    response = test_client.post("/memory/add", json=memory_data, headers=auth_headers)
    assert response.status_code == 201
    added_memory = response.json()
    assert added_memory["message"] == "Memory added successfully"
    assert "memory_id" in added_memory
    return added_memory["memory_id"]

def test_retrieve_memory(test_client: TestClient, auth_headers):
    memory_id = test_add_memory(test_client, auth_headers)
    retrieve_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "memory_id": memory_id
    }
    response = test_client.get("/memory/retrieve", params=retrieve_data, headers=auth_headers)
    assert response.status_code == 200
    memory = response.json()
    assert memory["content"] == "Test memory content"
    assert memory["metadata"] == {"key": "value"}

def test_search_memory(test_client: TestClient, auth_headers):
    test_add_memory(test_client, auth_headers)  # Add a memory to search for
    search_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "query": "Test memory",
        "limit": 5
    }
    response = test_client.post("/memory/search", json=search_data, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results["results"], list)
    assert len(results["results"]) > 0

def test_delete_memory(test_client: TestClient, auth_headers):
    memory_id = test_add_memory(test_client, auth_headers)
    delete_data = {
        "agent_id": str(UUID(int=0)),
        "memory_type": "SHORT_TERM",
        "memory_id": memory_id
    }
    response = test_client.delete("/memory/delete", params=delete_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Memory deleted successfully"

def test_memory_operation(test_client: TestClient, auth_headers):
    operation_data = {
        "agent_id": str(UUID(int=0)),
        "operation": "ADD",
        "memory_type": "SHORT_TERM",
        "data": {
            "content": "Test operation memory content",
            "metadata": {"operation": "test"}
        }
    }
    response = test_client.post("/memory/operate", json=operation_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "ADD operation completed successfully"
    assert "result" in result
```

# tests/test_api/test_main.py

```py
from fastapi.testclient import TestClient

def test_read_main(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SolidRusT Agentic API"}

```

# tests/test_api/test_function.py

```py
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_function(test_client: AsyncClient, auth_headers):
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
    response = await test_client.post("/function/register", json=function_data, headers=auth_headers)
    assert response.status_code == 201
    registered_function = response.json()
    assert registered_function["message"] == "Function registered successfully"
    assert "function_id" in registered_function
    return registered_function["function_id"]

@pytest.mark.asyncio
async def test_get_function(test_client: AsyncClient, auth_headers):
    function_id = await test_register_function(test_client, auth_headers)
    response = await test_client.get(f"/function/{function_id}", headers=auth_headers)
    assert response.status_code == 200
    function = response.json()
    assert function["name"] == "test_function"
    assert function["description"] == "A test function"

@pytest.mark.asyncio
async def test_update_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    update_data = {
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
    response = test_client.put(f"/function/update", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_function = response.json()
    assert updated_function["message"] == "Function updated successfully"

@pytest.mark.asyncio
async def test_delete_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    response = test_client.delete(f"/function/remove?agent_id=test_agent_id&function_id={function_id}", headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert result["message"] == "Function removed successfully"

@pytest.mark.asyncio
async def test_list_functions(test_client: TestClient, auth_headers):
    # Register a couple of functions first
    test_register_function(test_client, auth_headers)
    test_register_function(test_client, auth_headers)

    response = test_client.get("/function/available?agent_id=test_agent_id", headers=auth_headers)
    assert response.status_code == 200
    functions = response.json()
    assert isinstance(functions["functions"], list)
    assert len(functions["functions"]) >= 2  # We should have at least the two functions we just registered

@pytest.mark.asyncio
async def test_execute_function(test_client: TestClient, auth_headers):
    function_id = test_register_function(test_client, auth_headers)
    execution_data = {
        "agent_id": "test_agent_id",
        "function_name": "test_function",
        "parameters": {
            "param1": "test",
            "param2": 123
        }
    }
    response = test_client.post("/function/execute", json=execution_data, headers=auth_headers)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
```

# tests/test_api/test_agent.py

```py
import pytest
from fastapi.testclient import TestClient
from uuid import UUID

pytestmark = pytest.mark.asyncio

async def test_create_agent(test_client: TestClient, auth_headers):
    agent_data = {
        "agent_name": "Test Agent",
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
    response = test_client.post("/agent/create", json=agent_data, headers=auth_headers)
    assert response.status_code == 201
    created_agent = response.json()
    assert created_agent["message"] == "Agent created successfully"
    assert UUID(created_agent["agent_id"])
    return created_agent["agent_id"]

async def test_get_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.get(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 200
    agent = response.json()
    assert agent["agent_id"] == str(agent_id)
    assert agent["name"] == "Test Agent"

async def test_update_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    update_data = {
        "agent_config": {
            "temperature": 0.8
        }
    }
    response = test_client.patch(f"/agent/{agent_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    updated_agent = response.json()
    assert updated_agent["message"] == "Agent updated successfully"

async def test_delete_agent(test_client: TestClient, auth_headers):
    agent_id = test_create_agent(test_client, auth_headers)
    response = test_client.delete(f"/agent/{agent_id}", headers=auth_headers)
    assert response.status_code == 204

async def test_list_agents(test_client: TestClient, auth_headers):
    # Create a couple of agents first
    test_create_agent(test_client, auth_headers)
    test_create_agent(test_client, auth_headers)

    response = test_client.get("/agent/", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) >= 2  # We should have at least the two agents we just created
```

# tests/test_api/__init__.py

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
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

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
main_logger = setup_logger('main', settings.LOG_DIR + '/main.log')
agent_logger = setup_logger('agent', settings.LOG_DIR + '/agent.log')
memory_logger = setup_logger('memory', settings.LOG_DIR + '/memory.log')
llm_logger = setup_logger('llm', settings.LOG_DIR + '/llm.log')
function_logger = setup_logger('function', settings.LOG_DIR + '/function.log')  # New logger for function operations

```

# app/utils/auth.py

```py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == settings.API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
        )

def validate_api_key(api_key: str) -> bool:
    return api_key == settings.API_KEY
```

# app/utils/__init__.py

```py

```

# app/core/memory.py

```py
import asyncio
import json
from uuid import UUID, uuid4
from typing import Dict, Any, List, Optional
from redis import asyncio as aioredis
import chromadb
from chromadb.config import Settings
from app.api.models.memory import MemoryType, MemoryEntry, MemoryOperation
from app.api.models.agent import MemoryConfig
from app.utils.logging import memory_logger


class RedisMemory:
    def __init__(self, redis_url: str, agent_id: UUID):
        try:
            self.redis = aioredis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            self.agent_id = agent_id
            memory_logger.info(f"Redis connection established: {redis_url} for agent: {agent_id}")
        except Exception as e:
            memory_logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def add(self, key: str, value: str, expire: int = 3600):
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            await self.redis.set(full_key, value, ex=expire)
            memory_logger.debug(f"Added key to Redis: {full_key}")
        except Exception as e:
            memory_logger.error(f"Failed to add key to Redis: {full_key}. Error: {str(e)}")
            raise

    async def get(self, key: str) -> str:
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            value = await self.redis.get(full_key)
            memory_logger.debug(f"Retrieved key from Redis: {full_key}")
            return value
        except Exception as e:
            memory_logger.error(f"Failed to get key from Redis: {full_key}. Error: {str(e)}")
            raise

    async def delete(self, key: str):
        try:
            full_key = f"agent:{self.agent_id}:{key}"
            await self.redis.delete(full_key)
            memory_logger.debug(f"Deleted key from Redis: {full_key}")
        except Exception as e:
            memory_logger.error(f"Failed to delete key from Redis: {full_key}. Error: {str(e)}")
            raise

    async def get_recent(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            pattern = f"agent:{self.agent_id}:*"
            keys = await self.redis.keys(pattern)
            recent_memories = []
            for key in keys[-limit:]:
                value = await self.redis.get(key)
                if value:
                    recent_memories.append(json.loads(value))
            return recent_memories
        except Exception as e:
            memory_logger.error(f"Failed to get recent memories from Redis for agent {self.agent_id}: {str(e)}")
            raise

class VectorMemory:
    def __init__(self, collection_name: str):
        try:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(collection_name)
            memory_logger.info(f"ChromaDB collection initialized: {collection_name}")
        except Exception as e:
            memory_logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise

    async def add(self, id: str, content: str, metadata: Dict[str, Any] = {}):
        try:
            await asyncio.to_thread(self.collection.add,
                                    documents=[content],
                                    metadatas=[metadata],
                                    ids=[id])
            memory_logger.debug(f"Added document to ChromaDB: {id}")
        except Exception as e:
            memory_logger.error(f"Failed to add document to ChromaDB: {id}. Error: {str(e)}")
            raise

    async def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        try:
            results = await asyncio.to_thread(self.collection.query,
                                              query_texts=[query],
                                              n_results=n_results)
            memory_logger.debug(f"Searched ChromaDB: {query}")
            return [{"id": id, "content": doc, "metadata": meta}
                    for id, doc, meta in zip(results['ids'][0], results['documents'][0], results['metadatas'][0])]
        except Exception as e:
            memory_logger.error(f"Failed to search ChromaDB: {query}. Error: {str(e)}")
            raise


class MemorySystem:
    def __init__(self, agent_id: UUID, config: MemoryConfig):
        self.agent_id = agent_id
        self.config = config
        self.short_term = RedisMemory("redis://localhost:6379", agent_id)
        self.long_term = VectorMemory(f"agent_{agent_id}")
        memory_logger.info(f"MemorySystem initialized for agent: {agent_id}")

    async def add(self, memory_type: MemoryType, content: str, metadata: Dict[str, Any] = {}) -> str:
        try:
            memory_id = str(UUID.uuid4())
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
async def create_agent(name: str, config: AgentConfig, memory_config: MemoryConfig, initial_prompt: str) -> UUID:
    try:
        agent_id = uuid4()
        agent = Agent(agent_id, name, config, memory_config)
        agents[agent_id] = agent
        await agent.process_message(initial_prompt)
        agent_logger.info(f"Agent {name} (ID: {agent_id}) created successfully")
        return agent_id
    except Exception as e:
        agent_logger.error(f"Error creating Agent {name}: {str(e)}")
        raise

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

async def execute_function(agent_id: UUID, function_name: str, parameters: Dict[str, Any]) -> Any:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return await agent.execute_function(function_name, parameters)

async def get_available_functions(agent_id: UUID) -> List[FunctionDefinition]:
    agent = agents.get(agent_id)
    if not agent:
        agent_logger.error(f"No agent found with id: {agent_id}")
        raise ValueError(f"No agent found with id: {agent_id}")
    return agent.get_available_functions()

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

# app/api/__init__.py

```py

```

# .idea/inspectionProfiles/profiles_settings.xml

```xml
<component name="InspectionProjectProfileManager">
  <settings>
    <option name="USE_PROJECT_PROFILE" value="false" />
    <version value="1.0" />
  </settings>
</component>
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
from app.api.models.agent import AgentCreationRequest, AgentCreationResponse, AgentInfoResponse
from app.core.agent import create_agent, get_agent_info
from app.utils.auth import get_api_key
from app.utils.logging import agent_logger

router = APIRouter()

@router.post("/create", response_model=AgentCreationResponse, summary="Create a new agent")
async def create_agent_endpoint(request: AgentCreationRequest, api_key: str = Depends(get_api_key)):
    """
    Create a new agent with the given configuration.

    - **agent_name**: Name of the agent
    - **agent_config**: Configuration for the agent's LLM
    - **memory_config**: Configuration for the agent's memory systems
    - **initial_prompt**: The initial prompt to send to the agent upon creation
    """
    try:
        agent_logger.info(f"Received request to create agent: {request.agent_name}")
        agent_id = await create_agent(request.agent_name, request.agent_config, request.memory_config, request.initial_prompt)
        agent_logger.info(f"Agent created successfully: {agent_id}")
        return AgentCreationResponse(agent_id=agent_id, message="Agent created successfully")
    except Exception as e:
        agent_logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.get("/{agent_id}", response_model=AgentInfoResponse, summary="Get agent information")
async def get_agent_info_endpoint(agent_id: UUID, api_key: str = Depends(get_api_key)):
    """
    Retrieve information about a specific agent.

    - **agent_id**: The unique identifier of the agent
    """
    try:
        agent_logger.info(f"Received request to get info for agent: {agent_id}")
        agent_info = await get_agent_info(agent_id)
        if agent_info is None:
            agent_logger.warning(f"Agent not found: {agent_id}")
            raise HTTPException(status_code=404, detail="Agent not found")
        agent_logger.info(f"Successfully retrieved info for agent: {agent_id}")
        return agent_info
    except HTTPException:
        raise
    except Exception as e:
        agent_logger.error(f"Error retrieving agent info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving agent info: {str(e)}")

# Additional endpoints can be added here

```

# app/api/endpoints/__init__.py

```py
from .agent import router as agent_router
from .message import router as message_router
from .function import router as function_router
from .memory import router as memory_router

__all__ = ["agent_router", "message_router", "function_router", "memory_router"]

```

# .pytest_cache/v/cache/stepwise

```
[]
```

# .pytest_cache/v/cache/nodeids

```
[
  "tests/test_api/test_agent.py::test_create_agent",
  "tests/test_api/test_agent.py::test_delete_agent",
  "tests/test_api/test_agent.py::test_get_agent",
  "tests/test_api/test_agent.py::test_list_agents",
  "tests/test_api/test_agent.py::test_update_agent",
  "tests/test_api/test_function.py::test_delete_function",
  "tests/test_api/test_function.py::test_execute_function",
  "tests/test_api/test_function.py::test_get_function",
  "tests/test_api/test_function.py::test_list_functions",
  "tests/test_api/test_function.py::test_register_function",
  "tests/test_api/test_function.py::test_update_function",
  "tests/test_api/test_main.py::test_read_main",
  "tests/test_api/test_memory.py::test_add_memory",
  "tests/test_api/test_memory.py::test_delete_memory",
  "tests/test_api/test_memory.py::test_list_memories",
  "tests/test_api/test_memory.py::test_memory_operation",
  "tests/test_api/test_memory.py::test_retrieve_memory",
  "tests/test_api/test_memory.py::test_search_memory",
  "tests/test_api/test_memory.py::test_store_memory",
  "tests/test_api/test_memory.py::test_update_memory",
  "tests/test_api/test_message.py::test_clear_message_history",
  "tests/test_api/test_message.py::test_create_message",
  "tests/test_api/test_message.py::test_get_latest_message",
  "tests/test_api/test_message.py::test_get_message",
  "tests/test_api/test_message.py::test_get_message_history",
  "tests/test_api/test_message.py::test_list_messages",
  "tests/test_api/test_message.py::test_send_message",
  "tests/test_core/test_agent.py::test_agent_execute_function",
  "tests/test_core/test_agent.py::test_agent_get_available_functions",
  "tests/test_core/test_agent.py::test_agent_initialization",
  "tests/test_core/test_agent.py::test_agent_process_message"
]
```

# .pytest_cache/v/cache/lastfailed

```
{
  "tests/test_api/test_agent.py::test_create_agent": true,
  "tests/test_api/test_agent.py::test_get_agent": true,
  "tests/test_api/test_agent.py::test_update_agent": true,
  "tests/test_api/test_agent.py::test_delete_agent": true,
  "tests/test_api/test_agent.py::test_list_agents": true,
  "tests/test_api/test_function.py::test_update_function": true,
  "tests/test_api/test_function.py::test_delete_function": true,
  "tests/test_api/test_function.py::test_list_functions": true,
  "tests/test_api/test_memory.py::test_store_memory": true,
  "tests/test_api/test_memory.py::test_retrieve_memory": true,
  "tests/test_api/test_memory.py::test_update_memory": true,
  "tests/test_api/test_memory.py::test_delete_memory": true,
  "tests/test_api/test_memory.py::test_list_memories": true,
  "tests/test_api/test_message.py::test_create_message": true,
  "tests/test_api/test_message.py::test_get_message": true,
  "tests/test_api/test_message.py::test_list_messages": true,
  "tests/test_api/test_function.py::test_execute_function": true,
  "tests/test_api/test_memory.py::test_add_memory": true,
  "tests/test_api/test_memory.py::test_search_memory": true,
  "tests/test_api/test_memory.py::test_memory_operation": true,
  "tests/test_api/test_message.py::test_clear_message_history": true,
  "tests/test_api/test_message.py::test_get_latest_message": true,
  "tests/test_core/test_agent.py::test_agent_execute_function": true,
  "tests/test_core/test_agent.py::test_agent_get_available_functions": true,
  "tests/test_api/test_function.py::test_register_function": true,
  "tests/test_api/test_function.py::test_get_function": true,
  "tests/test_api/test_message.py::test_send_message": true,
  "tests/test_api/test_message.py::test_get_message_history": true,
  "tests/test_core/test_agent.py::test_agent_process_message": true
}
```

