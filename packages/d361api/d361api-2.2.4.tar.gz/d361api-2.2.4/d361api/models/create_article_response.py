"""
Compatibility module for CreateArticleResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.create_article_response.
"""

try:
    from d361api.d361api.create_article_response import CreateArticleResponse
    __all__ = ['CreateArticleResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CreateArticleResponse = getattr(d361api, 'CreateArticleResponse', None)
        if CreateArticleResponse is None:
            raise ImportError(f"Could not find CreateArticleResponse in d361api module")
        __all__ = ['CreateArticleResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CreateArticleResponse: {e}", ImportWarning)
        __all__ = []
