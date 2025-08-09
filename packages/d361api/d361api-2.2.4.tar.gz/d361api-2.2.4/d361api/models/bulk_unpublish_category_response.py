"""
Compatibility module for BulkUnpublishCategoryResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_unpublish_category_response.
"""

try:
    from d361api.d361api.bulk_unpublish_category_response import BulkUnpublishCategoryResponse
    __all__ = ['BulkUnpublishCategoryResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUnpublishCategoryResponse = getattr(d361api, 'BulkUnpublishCategoryResponse', None)
        if BulkUnpublishCategoryResponse is None:
            raise ImportError(f"Could not find BulkUnpublishCategoryResponse in d361api module")
        __all__ = ['BulkUnpublishCategoryResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUnpublishCategoryResponse: {e}", ImportWarning)
        __all__ = []
