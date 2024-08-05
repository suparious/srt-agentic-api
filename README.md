# SolidRusT Agentic API

SolidRusT Agentic API is a cutting-edge, highly scalable API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, featuring advanced memory management, dynamic function execution, and sophisticated message processing.

## Key Features

- Advanced agent creation and management
- Dual-layer memory system: Short-term (Redis) and long-term (ChromaDB) with efficient retrieval mechanisms
- Dynamic function calling capabilities with runtime registration
- Flexible LLM provider integration with intelligent fallback mechanism
- Highly scalable and modular architecture
- Comprehensive test suite with high code coverage
- Performance-optimized for high-load scenarios

## Project Structure

```plaintext
srt-agentic-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── memory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── add.py
│   │   │   │   ├── delete.py
│   │   │   │   ├── retrieve.py
│   │   │   │   ├── search.py
│   │   │   │   ├── operate.py
│   │   │   │   └── utils.py
│   │   │   ├── agent.py
│   │   │   ├── function.py
│   │   │   ├── memory.py
│   │   │   └── message.py
│   │   └── models/
│   ├── core/
│   │   ├── memory/
│   │   │   ├── __init__.py
│   │   │   ├── memory_system.py
│   │   │   ├── redis_memory.py
│   │   │   └── vector_memory.py
│   │   ├── agent.py
│   │   └── llm_provider.py
│   └── utils/
│       ├── auth.py
│       └── logging.py
├── docs/
├── examples/
│   ├── README.md
│   ├── python_example.py
│   └── javascript_example.js
├── logs/
├── tests/
│   ├── conftest.py
│   ├── test_api/
│   └── test_core/
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pytest.ini
└── README.md
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/SolidRusT/srt-agentic-api.git
   cd srt-agentic-api
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development and testing
   ```

4. Copy the `.env.example` file to `.env` and update the values:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your specific configuration values.

5. Set up the databases:
   - Ensure Redis is running for short-term memory operations.
   - Set up ChromaDB for long-term memory operations.

## Advanced LLM Provider Integration

SolidRusT Agentic API supports multiple LLM providers with an intelligent fallback mechanism. Configure your agents to use multiple providers in priority order for enhanced reliability.

Supported providers:
- OpenAI
- vLLM
- LlamaCpp
- TGI (Text Generation Inference)

Example configuration:

```json
{
  "agent_name": "MultiProviderAgent",
  "agent_config": {
    "llm_providers": [
      {
        "provider_type": "openai",
        "model_name": "gpt-3.5-turbo",
        "api_key": "your-openai-api-key"
      },
      {
        "provider_type": "vllm",
        "model_name": "llama-7b",
        "api_base": "http://your-vllm-server:8000"
      },
      {
        "provider_type": "llamacpp",
        "model_name": "llama-13b",
        "api_base": "http://your-llamacpp-server:8080"
      }
    ],
    "temperature": 0.7,
    "max_tokens": 150
  },
  "memory_config": {
    "use_long_term_memory": true,
    "use_redis_cache": true
  },
  "initial_prompt": "You are a helpful assistant."
}
```

## Running the Application

To run the application locally:

```
uvicorn app.main:app --reload
```

Access the API at `http://localhost:8000` and the API documentation at `http://localhost:8000/docs`.

## Development

### Running Tests

Execute the comprehensive test suite:

```
pytest --verbose --capture=no --cov=app --cov-report=term-missing
```

### Code Quality

Maintain code quality using pre-commit hooks:

```
pre-commit install
pre-commit run --all-files
```

### Performance Testing

Run load tests and profile memory usage:

```
locust -f tests/performance/locustfile.py
```

### Adding New Endpoints

1. Create a new file in the appropriate subdirectory under `app/api/endpoints/`.
2. Define necessary models in `app/api/models/`.
3. Implement core logic in `app/core/` if needed.
4. Update `app/main.py` to include your new endpoint router.
5. Write comprehensive tests for the new endpoint.

## Docker Deployment

Build and run the Docker container:

```
docker-compose up --build
```

For production deployment, refer to the `docker-compose.prod.yml` file.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and write tests to maintain or improve code coverage.
4. Run the test suite and ensure all tests pass.
5. Submit a pull request with a clear description of your changes.

## Documentation

For detailed API documentation, refer to the `/docs` endpoint when running the application. Additional technical documentation can be found in the `docs/` directory.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped shape and improve this project.
- Special thanks to the open-source communities behind FastAPI, Redis, and ChromaDB.

For any questions or support, please open an issue on the GitHub repository.
