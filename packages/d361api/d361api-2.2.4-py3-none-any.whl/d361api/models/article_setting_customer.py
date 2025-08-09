"""
Compatibility module for ArticleSettingCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_setting_customer.
"""

try:
    from d361api.d361api.article_setting_customer import ArticleSettingCustomer
    __all__ = ['ArticleSettingCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleSettingCustomer = getattr(d361api, 'ArticleSettingCustomer', None)
        if ArticleSettingCustomer is None:
            raise ImportError(f"Could not find ArticleSettingCustomer in d361api module")
        __all__ = ['ArticleSettingCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleSettingCustomer: {e}", ImportWarning)
        __all__ = []
