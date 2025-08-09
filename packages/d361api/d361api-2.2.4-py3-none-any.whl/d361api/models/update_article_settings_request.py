"""
Compatibility module for UpdateArticleSettingsRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_article_settings_request.
"""

try:
    from d361api.d361api.update_article_settings_request import UpdateArticleSettingsRequest
    __all__ = ['UpdateArticleSettingsRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateArticleSettingsRequest = getattr(d361api, 'UpdateArticleSettingsRequest', None)
        if UpdateArticleSettingsRequest is None:
            raise ImportError(f"Could not find UpdateArticleSettingsRequest in d361api module")
        __all__ = ['UpdateArticleSettingsRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateArticleSettingsRequest: {e}", ImportWarning)
        __all__ = []
