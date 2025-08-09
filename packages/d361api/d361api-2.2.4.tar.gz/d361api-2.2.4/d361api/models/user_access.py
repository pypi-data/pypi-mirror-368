"""
Compatibility module for UserAccess.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.user_access.
"""

try:
    from d361api.d361api.user_access import UserAccess
    __all__ = ['UserAccess']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UserAccess = getattr(d361api, 'UserAccess', None)
        if UserAccess is None:
            raise ImportError(f"Could not find UserAccess in d361api module")
        __all__ = ['UserAccess']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UserAccess: {e}", ImportWarning)
        __all__ = []
