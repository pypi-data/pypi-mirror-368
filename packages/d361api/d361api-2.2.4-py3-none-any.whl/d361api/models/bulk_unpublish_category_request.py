"""
Compatibility module for BulkUnpublishCategoryRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_unpublish_category_request.
"""

try:
    from d361api.d361api.bulk_unpublish_category_request import BulkUnpublishCategoryRequest
    __all__ = ['BulkUnpublishCategoryRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUnpublishCategoryRequest = getattr(d361api, 'BulkUnpublishCategoryRequest', None)
        if BulkUnpublishCategoryRequest is None:
            raise ImportError(f"Could not find BulkUnpublishCategoryRequest in d361api module")
        __all__ = ['BulkUnpublishCategoryRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUnpublishCategoryRequest: {e}", ImportWarning)
        __all__ = []
