"""
Compatibility module for CategoryAccessInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_access_info.
"""

try:
    from d361api.d361api.category_access_info import CategoryAccessInfo
    __all__ = ['CategoryAccessInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryAccessInfo = getattr(d361api, 'CategoryAccessInfo', None)
        if CategoryAccessInfo is None:
            raise ImportError(f"Could not find CategoryAccessInfo in d361api module")
        __all__ = ['CategoryAccessInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryAccessInfo: {e}", ImportWarning)
        __all__ = []
