"""
Compatibility module for ArticleVersionInfoCustomerResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_version_info_customer_response.
"""

try:
    from d361api.d361api.article_version_info_customer_response import ArticleVersionInfoCustomerResponse
    __all__ = ['ArticleVersionInfoCustomerResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleVersionInfoCustomerResponse = getattr(d361api, 'ArticleVersionInfoCustomerResponse', None)
        if ArticleVersionInfoCustomerResponse is None:
            raise ImportError(f"Could not find ArticleVersionInfoCustomerResponse in d361api module")
        __all__ = ['ArticleVersionInfoCustomerResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleVersionInfoCustomerResponse: {e}", ImportWarning)
        __all__ = []
