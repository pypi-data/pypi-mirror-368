"""
Compatibility module for Snippetresult.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.snippetresult.
"""

try:
    from d361api.d361api.snippetresult import Snippetresult
    __all__ = ['Snippetresult']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Snippetresult = getattr(d361api, 'Snippetresult', None)
        if Snippetresult is None:
            raise ImportError(f"Could not find Snippetresult in d361api module")
        __all__ = ['Snippetresult']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Snippetresult: {e}", ImportWarning)
        __all__ = []
