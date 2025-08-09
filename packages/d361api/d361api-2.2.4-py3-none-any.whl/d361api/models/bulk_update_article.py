"""
Compatibility module for BulkUpdateArticle.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_update_article.
"""

try:
    from d361api.d361api.bulk_update_article import BulkUpdateArticle
    __all__ = ['BulkUpdateArticle']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUpdateArticle = getattr(d361api, 'BulkUpdateArticle', None)
        if BulkUpdateArticle is None:
            raise ImportError(f"Could not find BulkUpdateArticle in d361api module")
        __all__ = ['BulkUpdateArticle']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUpdateArticle: {e}", ImportWarning)
        __all__ = []
