"""
Compatibility module for BulkUnpublishArticle.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_unpublish_article.
"""

try:
    from d361api.d361api.bulk_unpublish_article import BulkUnpublishArticle
    __all__ = ['BulkUnpublishArticle']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUnpublishArticle = getattr(d361api, 'BulkUnpublishArticle', None)
        if BulkUnpublishArticle is None:
            raise ImportError(f"Could not find BulkUnpublishArticle in d361api module")
        __all__ = ['BulkUnpublishArticle']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUnpublishArticle: {e}", ImportWarning)
        __all__ = []
