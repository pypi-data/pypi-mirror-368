"""
Compatibility module for Title.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.title.
"""

try:
    from d361api.d361api.title import Title
    __all__ = ['Title']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Title = getattr(d361api, 'Title', None)
        if Title is None:
            raise ImportError(f"Could not find Title in d361api module")
        __all__ = ['Title']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Title: {e}", ImportWarning)
        __all__ = []
