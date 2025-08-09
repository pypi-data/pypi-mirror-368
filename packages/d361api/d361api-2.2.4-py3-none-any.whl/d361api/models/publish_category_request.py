"""
Compatibility module for PublishCategoryRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.publish_category_request.
"""

try:
    from d361api.d361api.publish_category_request import PublishCategoryRequest
    __all__ = ['PublishCategoryRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        PublishCategoryRequest = getattr(d361api, 'PublishCategoryRequest', None)
        if PublishCategoryRequest is None:
            raise ImportError(f"Could not find PublishCategoryRequest in d361api module")
        __all__ = ['PublishCategoryRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import PublishCategoryRequest: {e}", ImportWarning)
        __all__ = []
