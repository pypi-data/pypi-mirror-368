"""
Compatibility module for RoleType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.role_type.
"""

try:
    from d361api.d361api.role_type import RoleType
    __all__ = ['RoleType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        RoleType = getattr(d361api, 'RoleType', None)
        if RoleType is None:
            raise ImportError(f"Could not find RoleType in d361api module")
        __all__ = ['RoleType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import RoleType: {e}", ImportWarning)
        __all__ = []
