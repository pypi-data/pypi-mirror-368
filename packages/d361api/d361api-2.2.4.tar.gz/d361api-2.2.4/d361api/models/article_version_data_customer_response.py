"""
Compatibility module for ArticleVersionDataCustomerResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_version_data_customer_response.
"""

try:
    from d361api.d361api.article_version_data_customer_response import ArticleVersionDataCustomerResponse
    __all__ = ['ArticleVersionDataCustomerResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleVersionDataCustomerResponse = getattr(d361api, 'ArticleVersionDataCustomerResponse', None)
        if ArticleVersionDataCustomerResponse is None:
            raise ImportError(f"Could not find ArticleVersionDataCustomerResponse in d361api module")
        __all__ = ['ArticleVersionDataCustomerResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleVersionDataCustomerResponse: {e}", ImportWarning)
        __all__ = []
