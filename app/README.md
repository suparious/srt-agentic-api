# SolidRusT Agentic API

```markdown
**Agentic**: Relating to or exhibiting the characteristics of an intelligent agent, including autonomy, decision-making capabilities, communication, task management, learning, and adaptation. An Agentic API facilitates the development and management of such intelligent agents, enabling them to perform tasks, interact with other systems, and improve over time.
```

SolidRusT Agentic API is a cutting-edge, highly scalable API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, featuring advanced memory management, dynamic function execution, and sophisticated message processing.

## Key Features

- Advanced agent creation and management
- Dual-layer memory system: Short-term (Redis) and long-term (ChromaDB) with efficient retrieval mechanisms
- Dynamic function calling capabilities with runtime registration
- Flexible LLM provider integration with intelligent fallback mechanism
- Highly scalable and modular architecture
- Performance-optimized for high-load scenarios

## Project Structure

The application code is currently organized into the following structure:

```plaintext
srt-agentic-api/
├── Dockerfile
├── README.md
├── TESTING.md
├── app
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── endpoints
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── function.py
│   │   │   ├── memory
│   │   │   │   ├── __init__.py
│   │   │   │   ├── add.py
│   │   │   │   ├── delete.py
│   │   │   │   ├── operate.py
│   │   │   │   ├── retrieve.py
│   │   │   │   ├── search.py
│   │   │   │   └── utils.py
│   │   │   ├── memory.py
│   │   │   └── message.py
│   │   └── models
│   │       ├── __init__.py
│   │       ├── agent.py
│   │       ├── function.py
│   │       ├── memory.py
│   │       └── message.py
│   ├── config.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── agent_manager.py
│   │   ├── function_manager.py
│   │   ├── llm_provider.py
│   │   └── memory
│   │       ├── __init__.py
│   │       ├── memory_operations.py
│   │       ├── memory_system.py
│   │       ├── memory_utils.py
│   │       ├── redis
│   │       │   ├── __init__.py
│   │       │   ├── cleanup.py
│   │       │   ├── connection.py
│   │       │   ├── memory_operations.py
│   │       │   └── search.py
│   │       ├── redis_memory.py
│   │       └── vector_memory.py
│   ├── main.py
│   └── utils
│       ├── __init__.py
│       ├── auth.py
│       └── logging.py
├── docker-compose.yml
├── examples
│   ├── README.md
│   ├── javascript_example.js
│   └── python_example.py
├── logs
│   ├── agent.log
│   ├── auth.log
│   ├── function.log
│   ├── llm.log
│   ├── main.log
│   ├── memory.log
│   └── test_results_detailed.txt
├── pytest.ini
└── requirements.txt
```
