"""
Compatibility module for CategoryVersionData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_version_data.
"""

try:
    from d361api.d361api.category_version_data import CategoryVersionData
    __all__ = ['CategoryVersionData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryVersionData = getattr(d361api, 'CategoryVersionData', None)
        if CategoryVersionData is None:
            raise ImportError(f"Could not find CategoryVersionData in d361api module")
        __all__ = ['CategoryVersionData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryVersionData: {e}", ImportWarning)
        __all__ = []
