"""
Compatibility module for BulkUpdateArticleResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_update_article_response.
"""

try:
    from d361api.d361api.bulk_update_article_response import BulkUpdateArticleResponse
    __all__ = ['BulkUpdateArticleResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkUpdateArticleResponse = getattr(d361api, 'BulkUpdateArticleResponse', None)
        if BulkUpdateArticleResponse is None:
            raise ImportError(f"Could not find BulkUpdateArticleResponse in d361api module")
        __all__ = ['BulkUpdateArticleResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkUpdateArticleResponse: {e}", ImportWarning)
        __all__ = []
