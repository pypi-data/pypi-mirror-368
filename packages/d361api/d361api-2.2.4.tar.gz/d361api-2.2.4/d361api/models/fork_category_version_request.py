"""
Compatibility module for ForkCategoryVersionRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.fork_category_version_request.
"""

try:
    from d361api.d361api.fork_category_version_request import ForkCategoryVersionRequest
    __all__ = ['ForkCategoryVersionRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ForkCategoryVersionRequest = getattr(d361api, 'ForkCategoryVersionRequest', None)
        if ForkCategoryVersionRequest is None:
            raise ImportError(f"Could not find ForkCategoryVersionRequest in d361api module")
        __all__ = ['ForkCategoryVersionRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ForkCategoryVersionRequest: {e}", ImportWarning)
        __all__ = []
