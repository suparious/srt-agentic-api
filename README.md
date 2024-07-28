# SolidRusT Agentic API

SolidRusT Agentic API is a powerful and flexible API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, including memory management, function execution, and message processing.

## Key Features

- Agent creation and management
- Short-term (Redis) and long-term (ChromaDB) memory systems
- Function calling capabilities
- Flexible LLM provider integration with fallback mechanism
- Scalable architecture

## Project Structure

```plaintext
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
├── examples/
│   ├── README.md
│   ├── python_example.py
│   └── javascript_example.js
├── logs/
├── tests/
├── requirements.txt
├── Dockerfile
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
   ```

4. Copy the `.env.example` file to `.env` and update the values:
   ```
   cp .env.example .env
   ```
   Edit the `.env` file with your specific configuration values.

5. Set up the database:
   - Ensure Redis is running for short-term memory operations.
   - Set up ChromaDB for long-term memory operations.

## LLM Provider Integration

SolidRusT Agentic API now supports multiple LLM providers with a fallback mechanism. This means you can configure your agents to use multiple providers in a priority order. If the primary provider fails, the system will automatically try the next provider in the list.

Supported providers:
- OpenAI
- vLLM
- LlamaCpp
- TGI (Text Generation Inference)

To configure multiple providers for an agent, use the following format in your agent creation request:

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

In this configuration, the system will first try to use OpenAI. If that fails, it will fall back to vLLM, and if that also fails, it will try LlamaCpp.

## Running the Application

To run the application locally:

```
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

## Examples

We provide example scripts to help you get started with the SolidRusT Agentic API. You can find these in the `examples/` directory:

- `README.md`: Contains curl commands for direct API interaction.
- `python_example.py`: A Python script demonstrating how to use the API.
- `javascript_example.js`: A JavaScript script showing API usage.

These examples cover basic operations such as creating an agent, sending messages, and retrieving agent information. They serve as a great starting point for AI scientists and university students to understand and experiment with our agentic API framework.

## Development

### Running Tests

To run the test suite:

```
pip install -U -r requirements-test.txt
pytest
```

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

```
docker build -t srt-agentic-api .
docker run -p 8000:8000 srt-agentic-api
```

For more detailed information about the API endpoints and request/response formats, please refer to the API documentation available at the `/docs` endpoint when running the application.
