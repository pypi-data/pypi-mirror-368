"""
Compatibility module for BulkPublishArticle.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_publish_article.
"""

try:
    from d361api.d361api.bulk_publish_article import BulkPublishArticle
    __all__ = ['BulkPublishArticle']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkPublishArticle = getattr(d361api, 'BulkPublishArticle', None)
        if BulkPublishArticle is None:
            raise ImportError(f"Could not find BulkPublishArticle in d361api module")
        __all__ = ['BulkPublishArticle']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkPublishArticle: {e}", ImportWarning)
        __all__ = []
