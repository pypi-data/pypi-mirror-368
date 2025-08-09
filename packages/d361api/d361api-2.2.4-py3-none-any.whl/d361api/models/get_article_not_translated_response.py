"""
Compatibility module for GetArticleNotTranslatedResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_article_not_translated_response.
"""

try:
    from d361api.d361api.get_article_not_translated_response import GetArticleNotTranslatedResponse
    __all__ = ['GetArticleNotTranslatedResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticleNotTranslatedResponse = getattr(d361api, 'GetArticleNotTranslatedResponse', None)
        if GetArticleNotTranslatedResponse is None:
            raise ImportError(f"Could not find GetArticleNotTranslatedResponse in d361api module")
        __all__ = ['GetArticleNotTranslatedResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticleNotTranslatedResponse: {e}", ImportWarning)
        __all__ = []
