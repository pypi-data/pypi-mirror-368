# GitHub Actions Setup Guide

Since the GitHub App doesn't have workflow permissions, you'll need to manually create/update the GitHub Actions workflow files. Here are the complete workflow files you need:

## 1. Enhanced Build & Test Workflow

Create/update `.github/workflows/push.yml`:

```yaml
name: Build & Test

on:
  push:
    branches: [main]
    tags-ignore: ["v*"]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write
  id-token: write

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  quality:
    name: Code Quality
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Ruff lint
        uses: astral-sh/ruff-action@v3
        with:
          version: "latest"
          args: "check --output-format=github"

      - name: Run Ruff Format
        uses: astral-sh/ruff-action@v3
        with:
          version: "latest"
          args: "format --check --respect-gitignore"

  test:
    name: Run Tests
    needs: quality
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: ${{ matrix.python-version }}
          enable-cache: true
          cache-suffix: ${{ matrix.os }}-${{ matrix.python-version }}

      - name: Install test dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system -e ".[test]"

      - name: Run tests with Pytest
        run: uv run pytest -n auto --maxfail=1 --disable-warnings --cov-report=xml --cov-config=pyproject.toml --cov=d361api --cov=test test/

      - name: Upload coverage report
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}-${{ matrix.os }}
          path: coverage.xml

  build:
    name: Build Distribution
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install build tools
        run: uv pip install --system build hatchling hatch-vcs

      - name: Build distributions
        run: uv run python -m build --outdir dist

      - name: Upload distribution artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-files
          path: dist/
          retention-days: 5
```

## 2. Enhanced Release Workflow

Create/update `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write
  id-token: write

jobs:
  test:
    name: Run Tests Before Release
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, windows-latest, macos-latest]
      fail-fast: false
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: ${{ matrix.python-version }}
          enable-cache: true
          cache-suffix: ${{ matrix.os }}-${{ matrix.python-version }}

      - name: Install test dependencies
        run: |
          uv pip install --system --upgrade pip
          uv pip install --system -e ".[test]"

      - name: Run tests
        run: uv run pytest -n auto --maxfail=1 --disable-warnings test/

  build:
    name: Build Distributions
    needs: test
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install UV
        uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          python-version: "3.12"
          enable-cache: true

      - name: Install build tools
        run: uv pip install --system build hatchling hatch-vcs

      - name: Build distributions
        run: uv run python -m build --outdir dist

      - name: Upload distribution artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist-${{ matrix.os }}
          path: dist/
          retention-days: 5

  release:
    name: Release to PyPI and GitHub
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/d361api
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Download all artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: dist-*
          merge-multiple: true
          path: dist/

      - name: Remove duplicate files
        run: |
          # Keep only unique files (in case of duplicates from different OS builds)
          cd dist
          for file in *.whl *.tar.gz; do
            if [ -f "$file" ]; then
              # Keep the first occurrence of each unique filename
              ls -la "$file"
            fi
          done

      - name: Verify distribution files
        run: |
          ls -la dist/
          test -n "$(find dist -name '*.whl')" || (echo "Wheel file missing" && exit 1)
          test -n "$(find dist -name '*.tar.gz')" || (echo "Source distribution missing" && exit 1)

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
          body: |
            ## What's Changed
            
            See the full changelog at: https://github.com/twardoch/d361api/blob/main/CHANGELOG.md
            
            ## Installation
            
            ```bash
            pip install d361api
            ```
            
            ## Supported Platforms
            
            - Linux (x86_64, arm64)
            - Windows (x86_64)
            - macOS (x86_64, arm64)
            
            ## Python Versions
            
            - Python 3.10+
            - Python 3.11
            - Python 3.12
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## 3. Setup Instructions

### Step 1: Add GitHub Secrets

Go to your GitHub repository settings → Secrets and variables → Actions, and add:

- `PYPI_TOKEN`: Your PyPI API token

### Step 2: Manual Workflow Creation

1. In your repository, create/update the files:
   - `.github/workflows/push.yml` (copy content from section 1 above)
   - `.github/workflows/release.yml` (copy content from section 2 above)

2. Commit and push these changes:
   ```bash
   git add .github/workflows/
   git commit -m "Add enhanced GitHub Actions workflows"
   git push
   ```

### Step 3: Test the Setup

1. **Test the build workflow**: Push any change to trigger the build workflow
2. **Test the release workflow**: Create a test release tag:
   ```bash
   git tag -a v2.2.2 -m "Test release v2.2.2"
   git push origin v2.2.2
   ```

## 4. Features of the New Workflows

### Build & Test Workflow (`push.yml`)
- **Triggers**: Push to main, PRs, manual dispatch
- **Quality checks**: Ruff linting and formatting
- **Multi-platform testing**: Ubuntu, Windows, macOS
- **Python versions**: 3.10, 3.11, 3.12
- **Test coverage**: Coverage reports with artifacts
- **Build verification**: Ensures package builds correctly

### Release Workflow (`release.yml`)
- **Triggers**: Git tag push (v*)
- **Pre-release testing**: Full test suite on all platforms
- **Multi-platform builds**: Builds on all platforms
- **PyPI publishing**: Automatic PyPI release
- **GitHub releases**: Creates GitHub release with artifacts
- **Release notes**: Auto-generated release notes

## 5. Benefits

- **Automated quality**: Every push is tested and linted
- **Multi-platform**: Works on Linux, Windows, macOS
- **Professional releases**: Automated PyPI and GitHub releases
- **Git-tag based**: Simple `git tag` triggers release
- **Comprehensive testing**: All Python versions and platforms
- **Artifact management**: Proper build artifact handling

## 6. Usage After Setup

Once the workflows are in place:

```bash
# Create a new release
make release-patch  # This will create and push a git tag
# GitHub Actions will automatically:
# 1. Run tests on all platforms
# 2. Build distributions
# 3. Publish to PyPI
# 4. Create GitHub release
```

The setup will provide professional-grade CI/CD with multiplatform support!