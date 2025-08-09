#!/bin/bash
# this_file: commit_without_workflows.sh
# Script to commit changes excluding GitHub Actions workflows

set -euo pipefail

echo "🔄 Committing changes (excluding GitHub Actions workflows)..."

# Add all files except GitHub Actions workflows
git add .
git reset .github/workflows/

# Check if there are any changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit (excluding workflows)"
    exit 0
fi

# Commit the changes
git commit -m "feat: implement git-tag-based semversioning with complete CI/CD setup

- Add git-tag-based semversioning using hatch-vcs
- Create comprehensive test suite with pytest
- Add local build and release scripts
- Implement CLI tool with d361api command
- Add development tools (Makefile, dev scripts)
- Create multiplatform GitHub Actions workflows (see GITHUB_ACTIONS_SETUP.md)
- Add comprehensive documentation and setup guides

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ Changes committed successfully!"
echo ""
echo "⚠️  Note: GitHub Actions workflows were not committed due to permissions."
echo "   Please manually create them using the guide in GITHUB_ACTIONS_SETUP.md"
echo ""
echo "Next steps:"
echo "1. Review GITHUB_ACTIONS_SETUP.md for workflow setup"
echo "2. Run: make setup (to set up development environment)"
echo "3. Run: make test (to run tests)"
echo "4. Run: make release-patch (to create a release)"