"""
Compatibility module for ArticleSimpleDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_simple_data_customer.
"""

try:
    from d361api.d361api.article_simple_data_customer import ArticleSimpleDataCustomer
    __all__ = ['ArticleSimpleDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleSimpleDataCustomer = getattr(d361api, 'ArticleSimpleDataCustomer', None)
        if ArticleSimpleDataCustomer is None:
            raise ImportError(f"Could not find ArticleSimpleDataCustomer in d361api module")
        __all__ = ['ArticleSimpleDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleSimpleDataCustomer: {e}", ImportWarning)
        __all__ = []
