"""
Compatibility module for UnpublishArticleRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.unpublish_article_request.
"""

try:
    from d361api.d361api.unpublish_article_request import UnpublishArticleRequest
    __all__ = ['UnpublishArticleRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UnpublishArticleRequest = getattr(d361api, 'UnpublishArticleRequest', None)
        if UnpublishArticleRequest is None:
            raise ImportError(f"Could not find UnpublishArticleRequest in d361api module")
        __all__ = ['UnpublishArticleRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UnpublishArticleRequest: {e}", ImportWarning)
        __all__ = []
