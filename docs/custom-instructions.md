Can you write me a good custom instructions prompt for development of this Python FastAPI srt-agentic-api AI Agentic API. Always write all the source files out in full, and use Claude Artifacts.

```plaintext
# Custom Instructions for srt-agentic-api Development

## Project Overview
The `srt-agentic-api` is a Python FastAPI-based API for creating, managing, and interacting with AI agents. It provides a robust framework for agent-based AI operations, including memory management, function execution, and message processing.

## Development Guidelines

### 1. Code Structure
- Maintain the existing project structure:
  ```
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
  ```
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
```
