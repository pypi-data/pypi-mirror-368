"""
Compatibility module for ArticleSettingCustomerResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_setting_customer_response.
"""

try:
    from d361api.d361api.article_setting_customer_response import ArticleSettingCustomerResponse
    __all__ = ['ArticleSettingCustomerResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleSettingCustomerResponse = getattr(d361api, 'ArticleSettingCustomerResponse', None)
        if ArticleSettingCustomerResponse is None:
            raise ImportError(f"Could not find ArticleSettingCustomerResponse in d361api module")
        __all__ = ['ArticleSettingCustomerResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleSettingCustomerResponse: {e}", ImportWarning)
        __all__ = []
