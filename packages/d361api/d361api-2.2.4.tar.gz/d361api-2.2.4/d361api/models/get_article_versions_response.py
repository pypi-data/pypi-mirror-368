"""
Compatibility module for GetArticleVersionsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_article_versions_response.
"""

try:
    from d361api.d361api.get_article_versions_response import GetArticleVersionsResponse
    __all__ = ['GetArticleVersionsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticleVersionsResponse = getattr(d361api, 'GetArticleVersionsResponse', None)
        if GetArticleVersionsResponse is None:
            raise ImportError(f"Could not find GetArticleVersionsResponse in d361api module")
        __all__ = ['GetArticleVersionsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticleVersionsResponse: {e}", ImportWarning)
        __all__ = []
