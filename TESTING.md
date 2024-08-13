# Running tests

Setup your python `3.12` virtual environment, update pip, then install the requirements.

   ```
   python -m pip install -U pip
   pip install -r requirements.txt
   pip install -r requirements-testing.txt
   ```

## Running all tests

Run all the tests and generate a shitload of output:

   ```
   pytest --verbose --capture=no --cov=app --cov-report=term-missing > logs/test_results_detailed.txt
   #pytest --verbose --capture=no > logs/test_results_detailed.txt
   ```

## Running Specific Tests

To run a specific test file:
`pytest tests/test_file_name.py`

To run a specific test function:
`pytest tests/test_file_name.py::test_function_name`

## Useful pytest Options

- Verbose output: `-v` or `--verbose`
- Show local variables in tracebacks: `-l` or `--showlocals`
- Exit on first failure: `-x` or `--exitfirst`
- Show slowest tests: `--durations=N` (where `N` is the number of slowest tests to show)

## Filtering Warnings

To ignore certain warnings:
`pytest -W ignore::DeprecationWarning`

## Focus on Errors

To show only errors and no warnings:
`pytest -p no:warnings`

## Running Tests with Coverage

To run tests with coverage report:
`pytest --cov=app --cov-report=term-missing`

To generate an HTML coverage report:
`pytest --cov=app --cov-report=html`

To generate an XML coverage report:
`pytest --cov=app --cov-report=xml`

## Other notes

To focus specifically on the memory system in our pytest suite, we can craft a command that targets the relevant test files and provides detailed output. Here's a recommended pytest command:

```bash
pytest -v -s --capture=no --log-cli-level=DEBUG -k "memory or Memory" tests/unit/core/memory tests/integration --cov=app/core/memory --cov-report=term-missing
```

Let's break down this command:



1. `-v`: Verbose mode, provides more detailed output.
2. `-s`: Allows print statements in tests to be displayed in the console.
3. `--capture=no`: Disables output capturing, showing all output in real-time.
4. `--log-cli-level=DEBUG`: Sets the logging level to DEBUG, giving us more detailed logs.
5. `-k "memory or Memory"`: This flag filters test files and functions that contain "memory" or "Memory" in their names.
6. `tests/unit/core/memory tests/integration`: Specifies the directories to search for tests, focusing on the memory-related unit tests and all integration tests.
7. `--cov=app/core/memory`: Enables coverage reporting, specifically for the `app/core/memory` directory.
8. `--cov-report=term-missing`: Generates a coverage report in the terminal, showing which lines are not covered by tests.

This command will:

1. Run all memory-related unit tests in the `tests/unit/core/memory` directory.
2. Run all integration tests (which may include memory-related integration tests).
3. Provide detailed output and logging information.
4. Show real-time print statements and logs.
5. Generate a coverage report specific to the memory system.

To make this even more focused, you could add additional path specifiers to target specific test files. For example:

```bash
pytest -v -s --capture=no --log-cli-level=DEBUG -k "memory or Memory" tests/unit/core/memory/test_redis_memory.py tests/unit/core/memory/test_vector_memory.py tests/unit/core/memory/test_memory_system.py tests/integration/test_redis_memory_integration.py --cov=app/core/memory --cov-report=term-missing
```

This command specifically targets the main memory-related test files.

Additionally, if you want to focus on a specific aspect of the memory system, you can further refine the `-k` parameter. For example, to focus on Redis-related memory tests:

```bash
pytest -v -s --capture=no --log-cli-level=DEBUG -k "redis and (memory or Memory)" tests/unit/core/memory tests/integration --cov=app/core/memory --cov-report=term-missing
```

These commands will help you focus specifically on the memory system, providing detailed output, logs, and coverage information to help identify and resolve any issues in the memory-related code.