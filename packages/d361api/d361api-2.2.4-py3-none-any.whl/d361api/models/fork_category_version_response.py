"""
Compatibility module for ForkCategoryVersionResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.fork_category_version_response.
"""

try:
    from d361api.d361api.fork_category_version_response import ForkCategoryVersionResponse
    __all__ = ['ForkCategoryVersionResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ForkCategoryVersionResponse = getattr(d361api, 'ForkCategoryVersionResponse', None)
        if ForkCategoryVersionResponse is None:
            raise ImportError(f"Could not find ForkCategoryVersionResponse in d361api module")
        __all__ = ['ForkCategoryVersionResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ForkCategoryVersionResponse: {e}", ImportWarning)
        __all__ = []
