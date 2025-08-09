#!/usr/bin/env python3
# this_file: test_basic_setup.py
"""Basic test to verify infrastructure setup."""

import os
import sys
import subprocess
import json

def test_git_setup():
    """Test git repository setup."""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git repository setup")
            
            # Check for existing tags
            result = subprocess.run(['git', 'tag', '--list'], 
                                  capture_output=True, text=True)
            tags = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"✅ Git tags found: {len(tags)} tags")
            if tags:
                latest_tag = tags[-1] if tags else "none"
                print(f"   Latest tag: {latest_tag}")
            
            return True
        else:
            print("❌ Not in a git repository")
            return False
    except Exception as e:
        print(f"❌ Git setup test failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist."""
    required_files = [
        'pyproject.toml',
        'README.md',
        'Makefile',
        'DEVELOPMENT.md',
        'scripts/build.sh',
        'scripts/test.sh',
        'scripts/release.sh',
        'scripts/dev-setup.sh',
        '.github/workflows/push.yml',
        '.github/workflows/release.yml',
        'd361api/__init__.py',
        'd361api/cli.py',
        'test/conftest.py',
        'test/test_version.py'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            missing.append(file)
    
    return len(missing) == 0

def test_scripts_executable():
    """Test that scripts are executable."""
    scripts = [
        'scripts/build.sh',
        'scripts/test.sh',
        'scripts/release.sh',
        'scripts/dev-setup.sh'
    ]
    
    all_executable = True
    for script in scripts:
        if os.path.exists(script) and os.access(script, os.X_OK):
            print(f"✅ {script} is executable")
        else:
            print(f"❌ {script} is not executable")
            all_executable = False
    
    return all_executable

def test_pyproject_toml():
    """Test pyproject.toml configuration."""
    if not os.path.exists('pyproject.toml'):
        print("❌ pyproject.toml missing")
        return False
    
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    required_sections = [
        '[build-system]',
        '[project]',
        '[project.scripts]',
        '[tool.hatch.version]',
        '[tool.ruff]',
        '[tool.pytest.ini_options]'
    ]
    
    all_present = True
    for section in required_sections:
        if section in content:
            print(f"✅ {section} found")
        else:
            print(f"❌ {section} missing")
            all_present = False
    
    return all_present

def test_package_structure():
    """Test package structure."""
    package_files = [
        'd361api/__init__.py',
        'd361api/__version__.py',
        'd361api/api_client.py',
        'd361api/configuration.py',
        'd361api/cli.py',
        'd361api/d361api/__init__.py'
    ]
    
    all_present = True
    for file in package_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_present = False
    
    return all_present

def test_version_file():
    """Test version file content."""
    version_file = 'd361api/__version__.py'
    if not os.path.exists(version_file):
        print("❌ Version file missing")
        return False
    
    with open(version_file, 'r') as f:
        content = f.read()
    
    if '__version__' in content:
        print("✅ Version file contains __version__")
        return True
    else:
        print("❌ Version file missing __version__")
        return False

def test_github_workflows():
    """Test GitHub Actions workflows."""
    workflows = [
        '.github/workflows/push.yml',
        '.github/workflows/release.yml'
    ]
    
    all_valid = True
    for workflow in workflows:
        if os.path.exists(workflow):
            with open(workflow, 'r') as f:
                content = f.read()
            
            if 'name:' in content and 'on:' in content and 'jobs:' in content:
                print(f"✅ {workflow} has valid structure")
            else:
                print(f"❌ {workflow} has invalid structure")
                all_valid = False
        else:
            print(f"❌ {workflow} missing")
            all_valid = False
    
    return all_valid

def test_makefile():
    """Test Makefile content."""
    if not os.path.exists('Makefile'):
        print("❌ Makefile missing")
        return False
    
    with open('Makefile', 'r') as f:
        content = f.read()
    
    required_targets = ['help', 'test', 'build', 'release-patch', 'clean']
    all_present = True
    
    for target in required_targets:
        if f'{target}:' in content:
            print(f"✅ Makefile target '{target}' found")
        else:
            print(f"❌ Makefile target '{target}' missing")
            all_present = False
    
    return all_present

def main():
    """Run all tests."""
    print("🔍 Testing d361api basic setup...")
    print("=" * 60)
    
    tests = [
        ("Git Setup", test_git_setup),
        ("File Structure", test_file_structure),
        ("Scripts Executable", test_scripts_executable),
        ("pyproject.toml", test_pyproject_toml),
        ("Package Structure", test_package_structure),
        ("Version File", test_version_file),
        ("GitHub Workflows", test_github_workflows),
        ("Makefile", test_makefile)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        try:
            result = test_func()
            results.append(result)
            if result:
                print(f"   ✅ {test_name} passed")
            else:
                print(f"   ❌ {test_name} failed")
        except Exception as e:
            print(f"   ❌ {test_name} error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if all(results):
        print("✅ All basic setup tests passed!")
        print("\n🚀 Ready for development!")
        print("\nNext steps:")
        print("1. Run: make setup")
        print("2. Run: make test")
        print("3. Run: make build")
        print("4. Create a release: make release-patch")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())