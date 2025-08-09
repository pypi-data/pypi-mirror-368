"""
Compatibility module for BulkUpdateCategoryContentResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_update_category_content_response.
"""

try:
    from d361api.d361api.bulk_update_category_content_response import BulkUpdateCategoryContentResponse
    __all__ = ['BulkUpdateCategoryContentResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUpdateCategoryContentResponse = getattr(d361api, 'BulkUpdateCategoryContentResponse', None)
        if BulkUpdateCategoryContentResponse is None:
            raise ImportError(f"Could not find BulkUpdateCategoryContentResponse in d361api module")
        __all__ = ['BulkUpdateCategoryContentResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUpdateCategoryContentResponse: {e}", ImportWarning)
        __all__ = []
