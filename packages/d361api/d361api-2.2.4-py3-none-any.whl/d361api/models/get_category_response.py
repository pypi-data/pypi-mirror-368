"""
Compatibility module for GetCategoryResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_category_response.
"""

try:
    from d361api.d361api.get_category_response import GetCategoryResponse
    __all__ = ['GetCategoryResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCategoryResponse = getattr(d361api, 'GetCategoryResponse', None)
        if GetCategoryResponse is None:
            raise ImportError(f"Could not find GetCategoryResponse in d361api module")
        __all__ = ['GetCategoryResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCategoryResponse: {e}", ImportWarning)
        __all__ = []
