"""
Compatibility module for UpdateArticleSettingsResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_article_settings_response_customer.
"""

try:
    from d361api.d361api.update_article_settings_response_customer import UpdateArticleSettingsResponseCustomer
    __all__ = ['UpdateArticleSettingsResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateArticleSettingsResponseCustomer = getattr(d361api, 'UpdateArticleSettingsResponseCustomer', None)
        if UpdateArticleSettingsResponseCustomer is None:
            raise ImportError(f"Could not find UpdateArticleSettingsResponseCustomer in d361api module")
        __all__ = ['UpdateArticleSettingsResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateArticleSettingsResponseCustomer: {e}", ImportWarning)
        __all__ = []
