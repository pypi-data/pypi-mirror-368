# this_file: test/test_version.py
"""Test version information."""

import re
import pytest
from d361api import __version__


def test_version_exists():
    """Test that version exists and is not empty."""
    assert __version__
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Test that version follows semantic versioning format."""
    # Allow for development versions with +g prefix
    version_pattern = r'^(\d+)\.(\d+)\.(\d+)(?:\.post\d+)?(?:\+g[a-f0-9]+)?$'
    assert re.match(version_pattern, __version__), f"Version {__version__} does not match semver pattern"


def test_version_components():
    """Test that version has valid numeric components."""
    # Extract main version parts (ignore post and git hash)
    main_version = __version__.split('.post')[0].split('+')[0]
    parts = main_version.split('.')
    
    assert len(parts) >= 3, f"Version {main_version} should have at least 3 parts"
    
    # Check that major, minor, patch are numeric
    for i, part in enumerate(parts[:3]):
        assert part.isdigit(), f"Version part {i} ({part}) should be numeric"
        assert int(part) >= 0, f"Version part {i} ({part}) should be non-negative"