"""
Compatibility module for UnpublishCategoryRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.unpublish_category_request.
"""

try:
    from d361api.d361api.unpublish_category_request import UnpublishCategoryRequest
    __all__ = ['UnpublishCategoryRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UnpublishCategoryRequest = getattr(d361api, 'UnpublishCategoryRequest', None)
        if UnpublishCategoryRequest is None:
            raise ImportError(f"Could not find UnpublishCategoryRequest in d361api module")
        __all__ = ['UnpublishCategoryRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UnpublishCategoryRequest: {e}", ImportWarning)
        __all__ = []
