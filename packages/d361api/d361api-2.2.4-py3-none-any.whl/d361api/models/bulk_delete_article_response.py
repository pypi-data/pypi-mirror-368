"""
Compatibility module for BulkDeleteArticleResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_delete_article_response.
"""

try:
    from d361api.d361api.bulk_delete_article_response import BulkDeleteArticleResponse
    __all__ = ['BulkDeleteArticleResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkDeleteArticleResponse = getattr(d361api, 'BulkDeleteArticleResponse', None)
        if BulkDeleteArticleResponse is None:
            raise ImportError(f"Could not find BulkDeleteArticleResponse in d361api module")
        __all__ = ['BulkDeleteArticleResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkDeleteArticleResponse: {e}", ImportWarning)
        __all__ = []
