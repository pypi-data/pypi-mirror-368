"""
Compatibility module for UpdateCategoryContentRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_category_content_request.
"""

try:
    from d361api.d361api.update_category_content_request import UpdateCategoryContentRequest
    __all__ = ['UpdateCategoryContentRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateCategoryContentRequest = getattr(d361api, 'UpdateCategoryContentRequest', None)
        if UpdateCategoryContentRequest is None:
            raise ImportError(f"Could not find UpdateCategoryContentRequest in d361api module")
        __all__ = ['UpdateCategoryContentRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateCategoryContentRequest: {e}", ImportWarning)
        __all__ = []
