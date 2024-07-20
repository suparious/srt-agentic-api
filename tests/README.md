# SolidRusT Agentic API Tests

This directory contains the tests for the SolidRusT Agentic API. The tests are organized into two main categories: API tests and Core tests.

## Directory Structure

```
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
```

- `conftest.py`: Contains pytest fixtures that can be used across multiple test files.
- `test_api/`: Contains tests for the API endpoints.
- `test_core/`: Contains tests for the core functionality of the application.

## Running Tests

To run all tests, use the following command from the root directory of the project:

```
pytest
```

To run tests in a specific file, use:

```
pytest tests/path/to/test_file.py
```

For example, to run the main API tests:

```
pytest tests/test_api/test_main.py
```

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

```python
from pydantic import BaseModel, ConfigDict

class YourModel(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    # Your model fields here
    model_name: str  # This field name is now allowed
```

To suppress warnings during tests (if you're not ready to address them immediately), you can add a `pytest.ini` file in the root of your project:

```ini
[pytest]
filterwarnings =
    ignore::DeprecationWarning:google._upb._message:
    ignore::pydantic.PydanticDeprecatedSince20
```

This will suppress the DeprecationWarnings from Google protobuf and the Pydantic v2 migration warnings during test runs.
