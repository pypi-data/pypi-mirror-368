"""
Compatibility module for BaseResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.base_response.
"""

try:
    from d361api.d361api.base_response import BaseResponse
    __all__ = ['BaseResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BaseResponse = getattr(d361api, 'BaseResponse', None)
        if BaseResponse is None:
            raise ImportError(f"Could not find BaseResponse in d361api module")
        __all__ = ['BaseResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BaseResponse: {e}", ImportWarning)
        __all__ = []
