#!/bin/bash
# this_file: scripts/test.sh
# Test script for d361api package

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "🧪 Starting test process..."

# Install test dependencies
echo "📦 Installing test dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[test]"

# Run code quality checks
echo "🔍 Running code quality checks..."
echo "  - Ruff format check..."
python3 -m ruff format --check --respect-gitignore .
echo "  - Ruff lint check..."
python3 -m ruff check --output-format=github .

# Run type checking
echo "🔬 Running type checking..."
python3 -m mypy d361api test

# Run tests
echo "🚀 Running tests..."
python3 -m pytest --cov-report=term-missing --cov-config=pyproject.toml --cov=d361api --cov=test test/

echo "✅ All tests passed!"