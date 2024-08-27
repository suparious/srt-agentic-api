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
srt-agentic-api/app
❯ tree -L 5 -I __pycache__
.
├── api
│   ├── endpoints
│   │   ├── agent.py
│   │   ├── function.py
│   │   ├── __init__.py
│   │   ├── memory
│   │   │   ├── add.py
│   │   │   ├── delete.py
│   │   │   ├── __init__.py
│   │   │   ├── operate.py
│   │   │   ├── retrieve.py
│   │   │   ├── search.py
│   │   │   └── utils.py
│   │   ├── memory.py
│   │   └── message.py
│   ├── __init__.py
│   └── models
│       ├── agent.py
│       ├── function.py
│       ├── __init__.py
│       ├── memory.py
│       └── message.py
├── config.py
├── core
│   ├── agent_manager.py
│   ├── agent.py
│   ├── function_manager.py
│   ├── __init__.py
│   ├── llm_provider.py
│   └── memory
│       ├── __init__.py
│       ├── memory_interface.py
│       ├── memory_operations.py
│       ├── memory_system.py
│       ├── memory_utils.py
│       ├── redis
│       │   ├── cleanup.py
│       │   ├── connection.py
│       │   ├── __init__.py
│       │   ├── memory_operations.py
│       │   └── search.py
│       ├── redis_memory.py
│       └── vector_memory.py
├── __init__.py
├── main.py
├── README.md
└── utils
    ├── auth.py
    ├── __init__.py
    └── logging.py
```
