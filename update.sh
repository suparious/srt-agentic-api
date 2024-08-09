#!/bin/bash
repo_home=$(pwd)
set -e

# Navigate to the docs directory
cd docs

# Remove old generated files
rm -rf _build

# Generate new documentation
make html

echo "Documentation updated successfully!"

# If you're using GitHub Pages, you can add a step here to commit and push the changes
# convert md to rst: `m2r2 project/current_status.md project/development_plan.md project/memory_system_tasks.md`

cd ${repo_home}

npx ai-digest
mv codebase.md ${HOME}/codebase/srt-agentic-api.md

cd tests
npx ai-digest
mv codebase.md ${HOME}/codebase/srt-agentic-api-tests.md

cd ${repo_home}

pytest -p no:warnings --verbose --capture=no --cov=app --cov-report=term-missing | tee logs/test_results_detailed.txt
