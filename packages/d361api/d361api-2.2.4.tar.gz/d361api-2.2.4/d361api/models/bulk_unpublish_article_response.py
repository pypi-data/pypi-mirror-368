"""
Compatibility module for BulkUnpublishArticleResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_unpublish_article_response.
"""

try:
    from d361api.d361api.bulk_unpublish_article_response import BulkUnpublishArticleResponse
    __all__ = ['BulkUnpublishArticleResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUnpublishArticleResponse = getattr(d361api, 'BulkUnpublishArticleResponse', None)
        if BulkUnpublishArticleResponse is None:
            raise ImportError(f"Could not find BulkUnpublishArticleResponse in d361api module")
        __all__ = ['BulkUnpublishArticleResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUnpublishArticleResponse: {e}", ImportWarning)
        __all__ = []
