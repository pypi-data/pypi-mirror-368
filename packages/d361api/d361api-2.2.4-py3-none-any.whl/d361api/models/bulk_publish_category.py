"""
Compatibility module for BulkPublishCategory.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_publish_category.
"""

try:
    from d361api.d361api.bulk_publish_category import BulkPublishCategory
    __all__ = ['BulkPublishCategory']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkPublishCategory = getattr(d361api, 'BulkPublishCategory', None)
        if BulkPublishCategory is None:
            raise ImportError(f"Could not find BulkPublishCategory in d361api module")
        __all__ = ['BulkPublishCategory']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkPublishCategory: {e}", ImportWarning)
        __all__ = []
