"""
Compatibility module for GetArticleSettingsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_article_settings_response.
"""

try:
    from d361api.d361api.get_article_settings_response import GetArticleSettingsResponse
    __all__ = ['GetArticleSettingsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticleSettingsResponse = getattr(d361api, 'GetArticleSettingsResponse', None)
        if GetArticleSettingsResponse is None:
            raise ImportError(f"Could not find GetArticleSettingsResponse in d361api module")
        __all__ = ['GetArticleSettingsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticleSettingsResponse: {e}", ImportWarning)
        __all__ = []
