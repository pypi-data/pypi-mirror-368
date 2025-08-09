"""
Compatibility module for UpdateArticleRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_article_request.
"""

try:
    from d361api.d361api.update_article_request import UpdateArticleRequest
    __all__ = ['UpdateArticleRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateArticleRequest = getattr(d361api, 'UpdateArticleRequest', None)
        if UpdateArticleRequest is None:
            raise ImportError(f"Could not find UpdateArticleRequest in d361api module")
        __all__ = ['UpdateArticleRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateArticleRequest: {e}", ImportWarning)
        __all__ = []
