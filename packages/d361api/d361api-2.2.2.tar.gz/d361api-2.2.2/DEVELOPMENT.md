# Development Guide

This guide explains how to set up and work with the d361api development environment.

## Quick Start

1. **Set up development environment:**
   ```bash
   make setup
   ```

2. **Run tests:**
   ```bash
   make test
   ```

3. **Build package:**
   ```bash
   make build
   ```

## Git-Tag Based Versioning

This project uses git tags for version management with semantic versioning:

### Version Format
- `v1.0.0` - Major release
- `v1.1.0` - Minor release  
- `v1.0.1` - Patch release

### Creating Releases

```bash
# Create patch release (1.0.0 -> 1.0.1)
make release-patch

# Create minor release (1.0.0 -> 1.1.0)
make release-minor

# Create major release (1.0.0 -> 2.0.0)
make release-major
```

The release script will:
1. Run all tests
2. Build the package
3. Create a git tag
4. Push the tag (triggers GitHub Actions)

### Manual Release Process

```bash
# Using the release script directly
./scripts/release.sh patch        # Creates and pushes tag
./scripts/release.sh minor false  # Creates tag but doesn't push
```

## Development Scripts

### Local Scripts

All scripts are located in the `scripts/` directory:

- `scripts/dev-setup.sh` - Set up development environment
- `scripts/test.sh` - Run complete test suite
- `scripts/build.sh` - Build distribution packages
- `scripts/release.sh` - Create and manage releases

### Make Commands

Use `make help` to see all available commands:

```bash
make help           # Show all commands
make setup          # Set up development environment
make test           # Run tests
make build          # Build package
make clean          # Clean build artifacts
make quality        # Run all quality checks
make release-patch  # Create patch release
```

## Testing

### Test Structure

```
test/
├── conftest.py          # Test configuration and fixtures
├── test_version.py      # Version validation tests
├── test_api_client.py   # API client tests
├── test_configuration.py # Configuration tests
├── test_models.py       # Model tests
├── test_apis.py         # API endpoint tests
└── test_integration.py  # Integration tests
```

### Running Tests

```bash
# Run all tests
make test

# Run quick tests (no coverage)
make test-quick

# Run with coverage report
make test-coverage

# Run specific test file
uv run pytest test/test_version.py -v

# Run tests with specific pattern
uv run pytest test/ -k "test_version" -v
```

## Code Quality

### Linting and Formatting

```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Run type checking
make typecheck

# Run all quality checks
make quality
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
make pre-commit-install

# Run pre-commit hooks manually
make pre-commit
```

## Build Process

### Local Build

```bash
# Build distributions
make build

# Clean build artifacts
make clean
```

### Build Outputs

The build process creates:
- `dist/*.whl` - Wheel distribution
- `dist/*.tar.gz` - Source distribution

## CLI Tool

The package includes a CLI tool for interacting with the Document360 API:

```bash
# Install in development mode
make dev-install

# Test CLI
make cli-test

# Use CLI
d361api --help
d361api project-versions
d361api articles PROJECT_VERSION_ID
```

## GitHub Actions

### Workflows

1. **Build & Test** (`.github/workflows/push.yml`)
   - Runs on every push to main
   - Tests on multiple Python versions and platforms
   - Uploads coverage reports

2. **Release** (`.github/workflows/release.yml`)
   - Runs on git tag push
   - Builds on multiple platforms
   - Publishes to PyPI
   - Creates GitHub release

### Multiplatform Support

The CI/CD pipeline tests and builds on:
- **Operating Systems**: Ubuntu, Windows, macOS
- **Python Versions**: 3.10, 3.11, 3.12
- **Architectures**: x86_64, arm64 (where supported)

## Environment Variables

### Development

```bash
# API configuration
export D361_API_TOKEN="your-api-token"
export D361_API_HOST="https://apihub.document360.io"  # Optional

# Development tools
export UV_PYTHON=python3.12  # Preferred Python version
```

### CI/CD

Required GitHub secrets:
- `PYPI_TOKEN` - PyPI API token for publishing

## Package Structure

```
d361api/
├── __init__.py          # Package initialization
├── __version__.py       # Version information (auto-generated)
├── cli.py              # CLI tool
├── api_client.py       # Main API client
├── configuration.py    # Configuration management
├── exceptions.py       # Exception classes
├── rest.py            # REST client
└── d361api/           # Generated API models
    ├── __init__.py
    ├── *.py           # Model classes
    └── ...
```

## Version Management

### Automatic Versioning

The project uses `hatch-vcs` for automatic version management:

- Version is determined from git tags
- Development versions include commit hash
- No manual version file editing needed

### Version Information

```python
import d361api
print(d361api.__version__)  # e.g., "2.2.1.post1+g8dc4c74"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've installed in development mode
   ```bash
   make dev-install
   ```

2. **Test failures**: Check that all dependencies are installed
   ```bash
   make setup
   ```

3. **Build errors**: Clean and rebuild
   ```bash
   make clean build
   ```

### Debug Mode

```bash
# Run with verbose output
uv run pytest -v --tb=long

# Debug specific test
uv run pytest test/test_version.py::test_version_exists -v -s
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Run quality checks: `make quality`
6. Submit a pull request

## Release Process

### Automated (Recommended)

```bash
make release-patch  # or release-minor, release-major
```

### Manual

```bash
# 1. Ensure clean working directory
git status

# 2. Run all tests
make test

# 3. Create tag
git tag -a v1.0.1 -m "Release v1.0.1"

# 4. Push tag
git push origin v1.0.1

# 5. GitHub Actions will handle the rest
```

## Support

- **Issues**: https://github.com/twardoch/d361api/issues
- **Discussions**: https://github.com/twardoch/d361api/discussions
- **API Documentation**: https://apidocs.document360.io/docs