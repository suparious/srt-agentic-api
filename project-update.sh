#!/bin/bash
## CI/CD script to:
# - generate Sphinx documentations from our docstrings
# - Create codebase summaries of the code and the test suites
# - Execute the full test suite
repo_home=$(pwd)

# Cleanup
## Remove old generated files
rm -rf ${repo_home}/docs/_build
rm ${repo_home}/logs/*
rm ${repo_home}/.coverage*

set -e

# Generate new documentation
cd ${repo_home}/docs
make html
echo "Documentation updated successfully!"
# If you're using GitHub Pages, you can add a step here to commit and push the changes
# convert md to rst: `m2r2 project/current_status.md project/development_plan.md project/memory_system_tasks.md`
cd ${repo_home}

# Generate codebase summary
#npx ai-digest --input ${repo_home} --output ${HOME}/codebase/srt-agentic-api.md
npx ai-digest --input ${repo_home}/app --output ${HOME}/codebase/srt-agentic-api-app.md
npx ai-digest --input ${repo_home}/tests --output ${HOME}/codebase/srt-agentic-api-tests.md

# Run the test suite
cd ${repo_home}
#pytest -p no:warnings --verbose --capture=no --cov=app --cov-report=term-missing | tee ${repo_home}/logs/test_results_detailed.txt
#pytest -v -s --capture=no --log-cli-level=DEBUG -k "memory or Memory" tests/unit/core/memory tests/integration tests/performance --cov=app/core/memory --cov-report=term-missing | tee ${repo_home}/logs/test_results_detailed.txt
pytest -v -s --capture=no --log-cli-level=DEBUG tests/integration tests/performance --cov=app/core/memory --cov-report=term-missing | tee ${repo_home}/logs/test_results_detailed.txt
