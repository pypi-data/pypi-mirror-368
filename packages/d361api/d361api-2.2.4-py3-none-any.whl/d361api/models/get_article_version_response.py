"""
Compatibility module for GetArticleVersionResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_article_version_response.
"""

try:
    from d361api.d361api.get_article_version_response import GetArticleVersionResponse
    __all__ = ['GetArticleVersionResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticleVersionResponse = getattr(d361api, 'GetArticleVersionResponse', None)
        if GetArticleVersionResponse is None:
            raise ImportError(f"Could not find GetArticleVersionResponse in d361api module")
        __all__ = ['GetArticleVersionResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticleVersionResponse: {e}", ImportWarning)
        __all__ = []
