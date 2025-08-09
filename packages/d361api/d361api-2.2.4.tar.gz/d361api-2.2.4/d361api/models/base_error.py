"""
Compatibility module for BaseError.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.base_error.
"""

try:
    from d361api.d361api.base_error import BaseError
    __all__ = ['BaseError']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BaseError = getattr(d361api, 'BaseError', None)
        if BaseError is None:
            raise ImportError(f"Could not find BaseError in d361api module")
        __all__ = ['BaseError']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BaseError: {e}", ImportWarning)
        __all__ = []
