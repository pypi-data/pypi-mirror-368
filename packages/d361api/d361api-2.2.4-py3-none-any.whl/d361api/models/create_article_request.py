"""
Compatibility module for CreateArticleRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.create_article_request.
"""

try:
    from d361api.d361api.create_article_request import CreateArticleRequest
    __all__ = ['CreateArticleRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CreateArticleRequest = getattr(d361api, 'CreateArticleRequest', None)
        if CreateArticleRequest is None:
            raise ImportError(f"Could not find CreateArticleRequest in d361api module")
        __all__ = ['CreateArticleRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CreateArticleRequest: {e}", ImportWarning)
        __all__ = []
