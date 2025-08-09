#!/bin/bash
# this_file: scripts/dev-setup.sh
# Development environment setup script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "🔧 Setting up development environment..."

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
uv venv --python 3.12

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Install package in development mode
echo "📦 Installing package in development mode..."
uv pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
uv pip install pre-commit
pre-commit install

echo "✅ Development environment setup completed!"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "Available commands:"
echo "  ./scripts/test.sh     - Run tests"
echo "  ./scripts/build.sh    - Build package"
echo "  ./scripts/release.sh  - Create release"