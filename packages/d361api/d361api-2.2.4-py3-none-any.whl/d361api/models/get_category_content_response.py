"""
Compatibility module for GetCategoryContentResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_category_content_response.
"""

try:
    from d361api.d361api.get_category_content_response import GetCategoryContentResponse
    __all__ = ['GetCategoryContentResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCategoryContentResponse = getattr(d361api, 'GetCategoryContentResponse', None)
        if GetCategoryContentResponse is None:
            raise ImportError(f"Could not find GetCategoryContentResponse in d361api module")
        __all__ = ['GetCategoryContentResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCategoryContentResponse: {e}", ImportWarning)
        __all__ = []
