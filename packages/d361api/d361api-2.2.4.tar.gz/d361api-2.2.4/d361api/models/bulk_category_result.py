"""
Compatibility module for BulkCategoryResult.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_category_result.
"""

try:
    from d361api.d361api.bulk_category_result import BulkCategoryResult
    __all__ = ['BulkCategoryResult']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkCategoryResult = getattr(d361api, 'BulkCategoryResult', None)
        if BulkCategoryResult is None:
            raise ImportError(f"Could not find BulkCategoryResult in d361api module")
        __all__ = ['BulkCategoryResult']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkCategoryResult: {e}", ImportWarning)
        __all__ = []
