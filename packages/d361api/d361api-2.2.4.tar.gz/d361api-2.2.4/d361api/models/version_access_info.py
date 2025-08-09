"""
Compatibility module for VersionAccessInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.version_access_info.
"""

try:
    from d361api.d361api.version_access_info import VersionAccessInfo
    __all__ = ['VersionAccessInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        VersionAccessInfo = getattr(d361api, 'VersionAccessInfo', None)
        if VersionAccessInfo is None:
            raise ImportError(f"Could not find VersionAccessInfo in d361api module")
        __all__ = ['VersionAccessInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import VersionAccessInfo: {e}", ImportWarning)
        __all__ = []
