#!/bin/bash
set -e

# Navigate to the docs directory
#cd docs

# Remove old generated files
rm -rf _build

# Generate new documentation
make html

echo "Documentation updated successfully!"

# If you're using GitHub Pages, you can add a step here to commit and push the changes
