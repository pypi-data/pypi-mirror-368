"""
Compatibility module for PublishArticleRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.publish_article_request.
"""

try:
    from d361api.d361api.publish_article_request import PublishArticleRequest
    __all__ = ['PublishArticleRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        PublishArticleRequest = getattr(d361api, 'PublishArticleRequest', None)
        if PublishArticleRequest is None:
            raise ImportError(f"Could not find PublishArticleRequest in d361api module")
        __all__ = ['PublishArticleRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import PublishArticleRequest: {e}", ImportWarning)
        __all__ = []
