#!/bin/bash
# this_file: scripts/release.sh
# Release script for d361api package

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

# Parse command line arguments
VERSION_TYPE="${1:-patch}"
PUSH_TAG="${2:-true}"

if [[ ! "$VERSION_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "❌ Invalid version type: $VERSION_TYPE"
    echo "Usage: $0 [major|minor|patch] [push_tag]"
    echo "  major: 1.0.0 -> 2.0.0"
    echo "  minor: 1.0.0 -> 1.1.0"
    echo "  patch: 1.0.0 -> 1.0.1"
    exit 1
fi

echo "🚀 Starting release process..."
echo "   Version type: $VERSION_TYPE"

# Get current version from git tags
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
echo "   Current version: $CURRENT_VERSION"

# Remove 'v' prefix for semver calculations
CURRENT_VERSION_NO_V="${CURRENT_VERSION#v}"

# Split version into parts
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION_NO_V"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Increment version based on type
case "$VERSION_TYPE" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="v${MAJOR}.${MINOR}.${PATCH}"
echo "   New version: $NEW_VERSION"

# Check if version already exists
if git tag -l | grep -q "^$NEW_VERSION$"; then
    echo "❌ Version $NEW_VERSION already exists!"
    exit 1
fi

# Check if working directory is clean
if ! git diff --quiet HEAD; then
    echo "❌ Working directory is not clean. Please commit or stash changes."
    exit 1
fi

# Ensure we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Not on main branch. Currently on: $CURRENT_BRANCH"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
"${SCRIPT_DIR}/test.sh"

# Build package
echo "🔨 Building package..."
"${SCRIPT_DIR}/build.sh"

# Create and push tag
echo "🏷️ Creating tag $NEW_VERSION..."
git tag -a "$NEW_VERSION" -m "Release $NEW_VERSION"

if [ "$PUSH_TAG" = "true" ]; then
    echo "📤 Pushing tag to remote..."
    git push origin "$NEW_VERSION"
    echo "✅ Tag pushed! GitHub Actions will handle the release."
else
    echo "⚠️ Tag created locally but not pushed. Run 'git push origin $NEW_VERSION' to trigger release."
fi

echo "✅ Release process completed!"
echo "   Version: $NEW_VERSION"
echo "   Tag: $(git describe --tags --abbrev=0)"