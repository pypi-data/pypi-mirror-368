"""
Compatibility module for Highlightresult.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.highlightresult.
"""

try:
    from d361api.d361api.highlightresult import Highlightresult
    __all__ = ['Highlightresult']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Highlightresult = getattr(d361api, 'Highlightresult', None)
        if Highlightresult is None:
            raise ImportError(f"Could not find Highlightresult in d361api module")
        __all__ = ['Highlightresult']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Highlightresult: {e}", ImportWarning)
        __all__ = []
