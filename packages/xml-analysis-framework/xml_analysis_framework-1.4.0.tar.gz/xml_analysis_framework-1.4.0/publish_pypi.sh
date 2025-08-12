#! /bin/bash

# This script is used to publish the xml-analysis-framework to PyPI.
# Clean previous builds to avoid uploading old versions
rm -rf dist/ build/
python -m build

# Upload to PyPI using either local .pypirc, global .pypirc, or TWINE_PASSWORD environment variable
if [ -f ".pypirc" ]; then
    python -m twine upload --config-file .pypirc dist/*
elif [ -n "$TWINE_PASSWORD" ]; then
    python -m twine upload --username __token__ --password "$TWINE_PASSWORD" dist/*
else
    python -m twine upload dist/*
fi
