"""
Compatibility module for BulkCreateCategoryResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_create_category_response.
"""

try:
    from d361api.d361api.bulk_create_category_response import BulkCreateCategoryResponse
    __all__ = ['BulkCreateCategoryResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkCreateCategoryResponse = getattr(d361api, 'BulkCreateCategoryResponse', None)
        if BulkCreateCategoryResponse is None:
            raise ImportError(f"Could not find BulkCreateCategoryResponse in d361api module")
        __all__ = ['BulkCreateCategoryResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkCreateCategoryResponse: {e}", ImportWarning)
        __all__ = []
