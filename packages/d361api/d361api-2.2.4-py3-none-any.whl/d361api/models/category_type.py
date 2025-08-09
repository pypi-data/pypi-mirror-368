"""
Compatibility module for CategoryType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_type.
"""

try:
    from d361api.d361api.category_type import CategoryType
    __all__ = ['CategoryType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryType = getattr(d361api, 'CategoryType', None)
        if CategoryType is None:
            raise ImportError(f"Could not find CategoryType in d361api module")
        __all__ = ['CategoryType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryType: {e}", ImportWarning)
        __all__ = []
