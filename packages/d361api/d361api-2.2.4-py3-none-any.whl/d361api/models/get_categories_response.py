"""
Compatibility module for GetCategoriesResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_categories_response.
"""

try:
    from d361api.d361api.get_categories_response import GetCategoriesResponse
    __all__ = ['GetCategoriesResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCategoriesResponse = getattr(d361api, 'GetCategoriesResponse', None)
        if GetCategoriesResponse is None:
            raise ImportError(f"Could not find GetCategoriesResponse in d361api module")
        __all__ = ['GetCategoriesResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCategoriesResponse: {e}", ImportWarning)
        __all__ = []
