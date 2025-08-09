"""
Compatibility module for Content.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.content.
"""

try:
    from d361api.d361api.content import Content
    __all__ = ['Content']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Content = getattr(d361api, 'Content', None)
        if Content is None:
            raise ImportError(f"Could not find Content in d361api module")
        __all__ = ['Content']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Content: {e}", ImportWarning)
        __all__ = []
