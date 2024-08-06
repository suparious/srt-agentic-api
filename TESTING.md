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
