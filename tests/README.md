# SolidRusT Agentic API Test Suite

This document provides comprehensive guidance for QA Engineers on running, maintaining, and extending the test suite for the SolidRusT Agentic API.

## Test Structure

The test suite is organized into the following categories:

```
tests
├── README.md
├── __init__.py
├── conftest.py
├── integration
│   ├── __init__.py
│   ├── test_main.py
│   └── test_redis_memory_integration.py
├── performance
│   ├── __init__.py
│   └── redis_benchmark.py
└── unit
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   ├── endpoints
    │   │   ├── __init__.py
    │   │   └── test_memory.py
    │   ├── models
    │   │   ├── __init__.py
    │   │   └── test_message_models.py
    │   ├── test_agent.py
    │   ├── test_function.py
    │   ├── test_memory.py
    │   └── test_message.py
    ├── core
    │   ├── __init__.py
    │   ├── memory
    │   │   ├── __init__.py
    │   │   ├── test_memory_system.py
    │   │   ├── test_redis_memory.py
    │   │   └── test_vector_memory.py
    │   ├── test_agent.py
    │   └── test_llm_provider.py
    └── test_async_setup.py
```

- `unit/`: Contains unit tests for core components and API endpoints.
- `integration/`: Houses integration tests that involve multiple components or external services.
- `conftest.py`: Defines pytest fixtures used across multiple test files.

## pytest Configuration

The project uses a `pytest.ini` file in the root directory to configure pytest behavior. The current configuration is:

```ini
[pytest]
asyncio_mode = auto
env_files = .env.test
```

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

```bash
pytest
```

### Specific Test Categories

Run unit tests only:
```bash
pytest tests/unit
```

Run integration tests only:
```bash
pytest tests/integration
```

### Individual Test Files

To run tests in a specific file:
```bash
pytest tests/path/to/test_file.py
```

Example:
```bash
pytest tests/unit/api/test_agent.py
```

### Test Selection by Markers

Use pytest markers to run specific types of tests:
```bash
pytest -m "integration"
```

## Writing and Maintaining Tests

1. Follow the existing directory structure when adding new tests.
2. Use descriptive names for test functions, prefixed with `test_`.
3. Utilize pytest fixtures from `conftest.py` for setup and teardown.
4. Aim for high test coverage, including edge cases and error scenarios.
5. Keep tests independent and idempotent.

## Debugging and Reporting Issues

When encountering test failures or unexpected behavior:

1. Run the failing test(s) with increased verbosity:
   ```bash
   pytest -vv path/to/failing_test.py
   ```

2. Use the `--pdb` flag to drop into the debugger on test failures:
   ```bash
   pytest --pdb path/to/failing_test.py
   ```

3. Generate a detailed test report:
   ```bash
   pytest --verbose --capture=no --cov=app --cov-report=term-missing > test_results_detailed.txt
   # pytest -p no:warnings --verbose --capture=no --cov=app --cov-report=term-missing | tee logs/test_results_detailed.txt
   # pytest -p no:warnings --capture=no --cov=app --cov-report=term-missing > test_results_detailed.txt
   ```

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

```ini
[pytest]
asyncio_mode = auto
env_files = .env.test
filterwarnings =
    ignore::DeprecationWarning:google._upb._message:
    ignore::pydantic.PydanticDeprecatedSince20
```

## Performance Considerations

- Unit tests should be fast and not depend on external services.
- Integration tests may be slower due to external dependencies.
- Use the `--durations=N` flag to identify slow tests:
  ```bash
  pytest --durations=10
  ```

## Extending the Test Suite

When adding new features or modifying existing ones:

1. Update or add unit tests in the appropriate `unit/` subdirectory.
2. Create or modify integration tests in the `integration/` directory.
3. Update `conftest.py` if new fixtures are required.
4. Ensure backward compatibility of existing tests unless intentionally breaking changes.

By following these guidelines, QA Engineers can effectively utilize, maintain, and extend the test suite, providing valuable feedback to the AI development team and ensuring the reliability of the SolidRusT Agentic API.
