# this_file: Makefile
# Makefile for d361api development

.PHONY: help install test build clean lint format typecheck coverage release setup dev-setup
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
UV := uv
VENV_DIR := .venv
DIST_DIR := dist
BUILD_DIR := build

help: ## Show this help message
	@echo "d361api Development Commands"
	@echo "==========================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@echo "🔧 Setting up development environment..."
	@./scripts/dev-setup.sh

install: ## Install package in development mode
	@echo "📦 Installing package in development mode..."
	@$(UV) pip install -e ".[dev]"

test: ## Run tests
	@echo "🧪 Running tests..."
	@./scripts/test.sh

test-quick: ## Run tests quickly (no coverage)
	@echo "⚡ Running quick tests..."
	@$(UV) run pytest -x --disable-warnings test/

test-coverage: ## Run tests with coverage report
	@echo "📊 Running tests with coverage..."
	@$(UV) run pytest --cov-report=html --cov-report=term-missing --cov-config=pyproject.toml --cov=d361api --cov=test test/

lint: ## Run linting
	@echo "🔍 Running linting..."
	@$(UV) run ruff check . --output-format=github

format: ## Format code
	@echo "✨ Formatting code..."
	@$(UV) run ruff format .

format-check: ## Check code formatting
	@echo "🔍 Checking code formatting..."
	@$(UV) run ruff format --check .

typecheck: ## Run type checking
	@echo "🔬 Running type checking..."
	@$(UV) run mypy d361api test

quality: format-check lint typecheck ## Run all quality checks

build: ## Build distribution packages
	@echo "🔨 Building distribution packages..."
	@./scripts/build.sh

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf $(DIST_DIR)/ $(BUILD_DIR)/ *.egg-info/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

release-patch: ## Create a patch release (e.g., 1.0.0 -> 1.0.1)
	@echo "🚀 Creating patch release..."
	@./scripts/release.sh patch

release-minor: ## Create a minor release (e.g., 1.0.0 -> 1.1.0)
	@echo "🚀 Creating minor release..."
	@./scripts/release.sh minor

release-major: ## Create a major release (e.g., 1.0.0 -> 2.0.0)
	@echo "🚀 Creating major release..."
	@./scripts/release.sh major

release-dry: ## Dry run release (create tag but don't push)
	@echo "🔍 Dry run release..."
	@./scripts/release.sh patch false

dev-install: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	@$(UV) pip install -e ".[dev]"

dev-update: ## Update development dependencies
	@echo "🔄 Updating development dependencies..."
	@$(UV) pip install --upgrade -e ".[dev]"

pre-commit: ## Run pre-commit hooks
	@echo "🪝 Running pre-commit hooks..."
	@$(UV) run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	@echo "🪝 Installing pre-commit hooks..."
	@$(UV) run pre-commit install

serve-docs: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@$(PYTHON) -m http.server 8000 -d docs/

check-deps: ## Check for dependency issues
	@echo "🔍 Checking dependencies..."
	@$(UV) pip check

security: ## Run security checks
	@echo "🔒 Running security checks..."
	@$(UV) run bandit -r d361api/

benchmark: ## Run performance benchmarks
	@echo "⚡ Running benchmarks..."
	@$(UV) run pytest test/ -k "benchmark" -v

# CLI related commands
cli-help: ## Show CLI help
	@echo "📖 CLI Help:"
	@$(UV) run python -m d361api.cli --help

cli-test: ## Test CLI functionality
	@echo "🧪 Testing CLI..."
	@$(UV) run python -m d361api.cli --version

# Docker related commands (if needed)
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	@docker build -t d361api:latest .

docker-test: ## Run tests in Docker
	@echo "🐳 Running tests in Docker..."
	@docker run --rm d361api:latest pytest

# Git related commands
git-clean: ## Clean git repository
	@echo "🧹 Cleaning git repository..."
	@git clean -fd

git-reset: ## Reset to last commit
	@echo "🔄 Resetting to last commit..."
	@git reset --hard HEAD

# Version info
version: ## Show version information
	@echo "📝 Version Information:"
	@echo "  Package: $$($(UV) run python -c 'import d361api; print(d361api.__version__)')"
	@echo "  Git: $$(git describe --tags --always --dirty)"
	@echo "  Python: $$($(PYTHON) --version)"

# Help with common workflows
workflow-dev: ## Development workflow
	@echo "🔄 Development workflow:"
	@echo "  1. make format"
	@echo "  2. make test"
	@echo "  3. make build"

workflow-release: ## Release workflow
	@echo "🚀 Release workflow:"
	@echo "  1. make quality"
	@echo "  2. make test"
	@echo "  3. make build"
	@echo "  4. make release-patch|minor|major"