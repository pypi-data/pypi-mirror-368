"""
Compatibility module for CategorySimpleData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_simple_data.
"""

try:
    from d361api.d361api.category_simple_data import CategorySimpleData
    __all__ = ['CategorySimpleData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategorySimpleData = getattr(d361api, 'CategorySimpleData', None)
        if CategorySimpleData is None:
            raise ImportError(f"Could not find CategorySimpleData in d361api module")
        __all__ = ['CategorySimpleData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategorySimpleData: {e}", ImportWarning)
        __all__ = []
