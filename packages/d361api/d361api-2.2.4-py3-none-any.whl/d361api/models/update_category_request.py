"""
Compatibility module for UpdateCategoryRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_category_request.
"""

try:
    from d361api.d361api.update_category_request import UpdateCategoryRequest
    __all__ = ['UpdateCategoryRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateCategoryRequest = getattr(d361api, 'UpdateCategoryRequest', None)
        if UpdateCategoryRequest is None:
            raise ImportError(f"Could not find UpdateCategoryRequest in d361api module")
        __all__ = ['UpdateCategoryRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateCategoryRequest: {e}", ImportWarning)
        __all__ = []
