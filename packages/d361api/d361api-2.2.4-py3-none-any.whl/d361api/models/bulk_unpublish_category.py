"""
Compatibility module for BulkUnpublishCategory.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_unpublish_category.
"""

try:
    from d361api.d361api.bulk_unpublish_category import BulkUnpublishCategory
    __all__ = ['BulkUnpublishCategory']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUnpublishCategory = getattr(d361api, 'BulkUnpublishCategory', None)
        if BulkUnpublishCategory is None:
            raise ImportError(f"Could not find BulkUnpublishCategory in d361api module")
        __all__ = ['BulkUnpublishCategory']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUnpublishCategory: {e}", ImportWarning)
        __all__ = []
