#!/bin/bash
# this_file: scripts/build.sh
# Build script for d361api package

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "🔨 Starting build process..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Install build dependencies
echo "📦 Installing build dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install build hatchling hatch-vcs

# Build distributions
echo "🏗️ Building distributions..."
python3 -m build --outdir dist

# Verify build
echo "✅ Verifying build..."
ls -la dist/
test -n "$(find dist -name '*.whl')" || (echo "❌ Wheel file missing" && exit 1)
test -n "$(find dist -name '*.tar.gz')" || (echo "❌ Source distribution missing" && exit 1)

echo "✅ Build completed successfully!"
echo "📁 Files created:"
ls -la dist/