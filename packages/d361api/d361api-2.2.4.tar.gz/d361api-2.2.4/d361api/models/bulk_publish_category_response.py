"""
Compatibility module for BulkPublishCategoryResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_publish_category_response.
"""

try:
    from d361api.d361api.bulk_publish_category_response import BulkPublishCategoryResponse
    __all__ = ['BulkPublishCategoryResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkPublishCategoryResponse = getattr(d361api, 'BulkPublishCategoryResponse', None)
        if BulkPublishCategoryResponse is None:
            raise ImportError(f"Could not find BulkPublishCategoryResponse in d361api module")
        __all__ = ['BulkPublishCategoryResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkPublishCategoryResponse: {e}", ImportWarning)
        __all__ = []
