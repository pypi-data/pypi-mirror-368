"""
Compatibility module for BaseResponseContext.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.base_response_context.
"""

try:
    from d361api.d361api.base_response_context import BaseResponseContext
    __all__ = ['BaseResponseContext']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BaseResponseContext = getattr(d361api, 'BaseResponseContext', None)
        if BaseResponseContext is None:
            raise ImportError(f"Could not find BaseResponseContext in d361api module")
        __all__ = ['BaseResponseContext']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BaseResponseContext: {e}", ImportWarning)
        __all__ = []
