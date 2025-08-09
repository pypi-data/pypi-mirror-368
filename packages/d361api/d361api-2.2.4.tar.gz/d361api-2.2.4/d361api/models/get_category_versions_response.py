"""
Compatibility module for GetCategoryVersionsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_category_versions_response.
"""

try:
    from d361api.d361api.get_category_versions_response import GetCategoryVersionsResponse
    __all__ = ['GetCategoryVersionsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCategoryVersionsResponse = getattr(d361api, 'GetCategoryVersionsResponse', None)
        if GetCategoryVersionsResponse is None:
            raise ImportError(f"Could not find GetCategoryVersionsResponse in d361api module")
        __all__ = ['GetCategoryVersionsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCategoryVersionsResponse: {e}", ImportWarning)
        __all__ = []
