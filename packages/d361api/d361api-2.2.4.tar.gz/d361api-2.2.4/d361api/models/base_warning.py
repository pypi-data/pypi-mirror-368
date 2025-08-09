"""
Compatibility module for BaseWarning.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.base_warning.
"""

try:
    from d361api.d361api.base_warning import BaseWarning
    __all__ = ['BaseWarning']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BaseWarning = getattr(d361api, 'BaseWarning', None)
        if BaseWarning is None:
            raise ImportError(f"Could not find BaseWarning in d361api module")
        __all__ = ['BaseWarning']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BaseWarning: {e}", ImportWarning)
        __all__ = []
