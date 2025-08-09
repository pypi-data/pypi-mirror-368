"""
Compatibility module for CategoryMeta.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_meta.
"""

try:
    from d361api.d361api.category_meta import CategoryMeta
    __all__ = ['CategoryMeta']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryMeta = getattr(d361api, 'CategoryMeta', None)
        if CategoryMeta is None:
            raise ImportError(f"Could not find CategoryMeta in d361api module")
        __all__ = ['CategoryMeta']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryMeta: {e}", ImportWarning)
        __all__ = []
