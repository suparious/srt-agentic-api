# Advanced Test Improvement Plan for srt-agentic-api

## Current Status
- Test coverage: 63%
- Passing tests: ~50%
- Target: 80% code coverage with all tests passing

## Critical Issues and Improvement Strategies

### 1. Redis Memory Implementation (High Priority)
The most frequent errors are related to the Redis memory implementation, particularly in the `add` method.

**Issues:**
- `AttributeError: 'str' object has no attribute 'content'` in `RedisMemory.add()`
- Errors in Redis connection and cleanup

**Action Items:**
1. Review and refactor `app/core/memory/redis_memory.py`:
   - Fix the `add` method to correctly handle `MemoryEntry` objects
   - Implement proper error handling for Redis connections
2. Update tests in `tests/core/memory/test_redis_memory.py`:
   - Ensure mock objects correctly simulate Redis behavior
   - Add more granular tests for edge cases and error scenarios

### 2. Agent Implementation (High Priority)
Several tests fail due to issues with the Agent implementation.

**Issues:**
- `'LLMProviderConfig' object is not subscriptable`
- `'UUID' object has no attribute 'name'`
- `'UUID' object has no attribute 'available_function_ids'`

**Action Items:**
1. Refactor `app/core/agent.py`:
   - Review and fix the `LLMProviderConfig` usage
   - Implement proper attribute access for UUID objects
   - Add necessary attributes or methods to the Agent class
2. Update tests in `tests/test_api/test_agent.py` and `tests/test_core/test_agent.py`:
   - Adjust test setup to match the new Agent implementation
   - Add more unit tests for Agent methods

### 3. Async Testing and Event Loop Management (Medium Priority)
There are issues with async testing and event loop management.

**Issues:**
- RuntimeWarnings about coroutines never awaited
- Errors about tasks attached to different event loops

**Action Items:**
1. Review and update `tests/conftest.py`:
   - Implement proper async fixture management
   - Ensure consistent event loop usage across tests
2. Refactor async tests:
   - Use `pytest.mark.asyncio` consistently
   - Implement proper cleanup for async resources

### 4. LLM Provider Integration (Medium Priority)
LLM provider integration tests are failing.

**Issues:**
- Mocked LLM providers failing in sequence

**Action Items:**
1. Review and update `app/core/llm_provider.py`:
   - Implement more robust error handling and fallback mechanisms
2. Enhance tests in `tests/test_core/test_llm_provider.py`:
   - Implement more realistic mock scenarios
   - Test each provider individually and in combination

### 5. API Endpoint Implementation (Medium Priority)
Many API endpoint tests are failing.

**Issues:**
- Incorrect status codes returned
- Errors in request handling

**Action Items:**
1. Review and update API endpoint implementations in `app/api/endpoints/`:
   - Ensure proper error handling and status code returns
   - Implement input validation using Pydantic models
2. Enhance API tests in `tests/test_api/`:
   - Add more comprehensive test cases
   - Implement proper setup and teardown for API tests

### 6. Memory System Integration (Low Priority)
There are issues with the integration of different memory systems.

**Issues:**
- Errors in memory addition and retrieval across different memory types

**Action Items:**
1. Review and update `app/core/memory/memory_system.py`:
   - Ensure proper integration between short-term and long-term memory
   - Implement robust error handling for memory operations
2. Enhance tests in `tests/test_core/test_memory.py`:
   - Add more integration tests for memory system operations
   - Test edge cases and error scenarios

## Implementation Plan

1. **Week 1: Redis Memory and Agent Implementation**
   - Day 1-2: Refactor Redis memory implementation
   - Day 3-4: Update Agent implementation
   - Day 5: Update corresponding tests

2. **Week 2: Async Testing and LLM Provider Integration**
   - Day 1-2: Refactor async testing setup
   - Day 3-4: Enhance LLM provider integration
   - Day 5: Update corresponding tests

3. **Week 3: API Endpoint Implementation and Memory System Integration**
   - Day 1-3: Refactor API endpoints
   - Day 4-5: Enhance memory system integration
   - Throughout: Update corresponding tests

4. **Week 4: Final Testing and Coverage Improvement**
   - Day 1-3: Add missing tests to improve coverage
   - Day 4-5: Final review and optimization

## Monitoring and Reporting

- Implement daily test runs and coverage reports
- Review progress weekly and adjust the plan as needed
- Create a dashboard to visualize test coverage and passing/failing tests over time

By following this plan, we should be able to achieve the goal of 80% code coverage with all tests passing. Regular reviews and adjustments will be crucial to ensure we're making steady progress towards our goal.
