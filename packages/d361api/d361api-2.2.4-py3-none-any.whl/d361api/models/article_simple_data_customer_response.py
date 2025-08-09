"""
Compatibility module for ArticleSimpleDataCustomerResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_simple_data_customer_response.
"""

try:
    from d361api.d361api.article_simple_data_customer_response import ArticleSimpleDataCustomerResponse
    __all__ = ['ArticleSimpleDataCustomerResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleSimpleDataCustomerResponse = getattr(d361api, 'ArticleSimpleDataCustomerResponse', None)
        if ArticleSimpleDataCustomerResponse is None:
            raise ImportError(f"Could not find ArticleSimpleDataCustomerResponse in d361api module")
        __all__ = ['ArticleSimpleDataCustomerResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleSimpleDataCustomerResponse: {e}", ImportWarning)
        __all__ = []
