#!/usr/bin/env python3
# this_file: test_setup.py
"""Simple test to verify the setup works."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_version():
    """Test that version can be imported."""
    try:
        from d361api import __version__
        print(f"✅ Version import successful: {__version__}")
        return True
    except ImportError as e:
        print(f"❌ Version import failed: {e}")
        return False

def test_configuration():
    """Test that configuration can be imported."""
    try:
        from d361api.configuration import Configuration
        config = Configuration()
        print(f"✅ Configuration import successful: {config.host}")
        return True
    except ImportError as e:
        print(f"❌ Configuration import failed: {e}")
        return False

def test_scripts():
    """Test that scripts exist and are executable."""
    scripts = [
        'scripts/build.sh',
        'scripts/test.sh', 
        'scripts/release.sh',
        'scripts/dev-setup.sh'
    ]
    
    all_good = True
    for script in scripts:
        if os.path.exists(script) and os.access(script, os.X_OK):
            print(f"✅ Script exists and is executable: {script}")
        else:
            print(f"❌ Script missing or not executable: {script}")
            all_good = False
    
    return all_good

def test_github_actions():
    """Test that GitHub Actions workflows exist."""
    workflows = [
        '.github/workflows/push.yml',
        '.github/workflows/release.yml'
    ]
    
    all_good = True
    for workflow in workflows:
        if os.path.exists(workflow):
            print(f"✅ GitHub Actions workflow exists: {workflow}")
        else:
            print(f"❌ GitHub Actions workflow missing: {workflow}")
            all_good = False
    
    return all_good

def test_makefile():
    """Test that Makefile exists."""
    if os.path.exists('Makefile'):
        print("✅ Makefile exists")
        return True
    else:
        print("❌ Makefile missing")
        return False

def test_pyproject():
    """Test that pyproject.toml has expected content."""
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml missing")
        return False
    
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    checks = [
        ('hatch-vcs', 'Version control system'),
        ('d361api.cli:main', 'CLI entry point'),
        ('pytest', 'Testing framework'),
        ('ruff', 'Linting tool')
    ]
    
    all_good = True
    for check, desc in checks:
        if check in content:
            print(f"✅ {desc} found in pyproject.toml")
        else:
            print(f"❌ {desc} missing from pyproject.toml")
            all_good = False
    
    return all_good

def main():
    """Run all tests."""
    print("🔍 Testing d361api setup...")
    print("=" * 50)
    
    tests = [
        test_version,
        test_configuration,
        test_scripts,
        test_github_actions,
        test_makefile,
        test_pyproject
    ]
    
    results = [test() for test in tests]
    
    print("=" * 50)
    if all(results):
        print("✅ All tests passed! Setup is complete.")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())