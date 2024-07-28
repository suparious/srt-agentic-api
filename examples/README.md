# SolidRusT Agentic API Examples

This folder contains examples to help you get started with the SolidRusT Agentic API. Below you'll find curl commands for direct API interaction, as well as Python and JavaScript examples.

## Table of Contents

1. [Curl Commands](#curl-commands)
2. [Python Example](#python-example)
3. [JavaScript Example](#javascript-example)

## Curl Commands

### Create an Agent

```bash
curl -X POST http://localhost:8000/agent/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "agent_name": "TestAgent",
    "agent_config": {
      "llm_provider": "openai",
      "model_name": "gpt-3.5-turbo",
      "temperature": 0.7,
      "max_tokens": 150,
      "memory_config": {
        "use_long_term_memory": true,
        "use_redis_cache": true
      }
    },
    "memory_config": {
      "use_long_term_memory": true,
      "use_redis_cache": true
    },
    "initial_prompt": "You are a helpful assistant."
  }'
```

### Send a Message to an Agent

```bash
curl -X POST http://localhost:8000/message/send \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "agent_id": "your_agent_id_here",
    "content": "Hello, what can you help me with today?"
  }'
```

### Get Agent Information

```bash
curl -X GET http://localhost:8000/agent/your_agent_id_here \
  -H "X-API-Key: your_api_key_here"
```

## Python Example

See the [python_example.py](./python_example.py) file for a complete Python example.

Using multiple providers as fallback:

```python
from app.core.llm_provider import create_llm_provider

provider_configs = [
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
]

llm_provider = create_llm_provider(provider_configs)
```

## JavaScript Example

See the [javascript_example.js](./javascript_example.js) file for a complete JavaScript example.

For more detailed information about the API endpoints and request/response formats, please refer to the main API documentation.