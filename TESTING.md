# Instructions for Running Tests

1. Open a terminal window.
2. Navigate to the root directory of the srt-agentic-api project.
3. Ensure that all dependencies are installed by running:
   ```
   pip install -r requirements.txt
   pip install -r requirements-testing.txt
   ```
4. Run the following command to execute the tests and capture the output:
   ```
   pytest --verbose --capture=no --cov=app --cov-report=term-missing > logs/test_results_detailed.txt
   #pytest --verbose --capture=no > logs/test_results_detailed.txt
   ```
5. Once the command completes, please provide the contents of the `logs/test_results_detailed.txt` file as an artifact in your next message.

Note: If you encounter any errors or issues while running the tests, please include those details in your response as well.