"""
Compatibility module for BulkDeleteCategoryVersionResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_delete_category_version_response.
"""

try:
    from d361api.d361api.bulk_delete_category_version_response import BulkDeleteCategoryVersionResponse
    __all__ = ['BulkDeleteCategoryVersionResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkDeleteCategoryVersionResponse = getattr(d361api, 'BulkDeleteCategoryVersionResponse', None)
        if BulkDeleteCategoryVersionResponse is None:
            raise ImportError(f"Could not find BulkDeleteCategoryVersionResponse in d361api module")
        __all__ = ['BulkDeleteCategoryVersionResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkDeleteCategoryVersionResponse: {e}", ImportWarning)
        __all__ = []
