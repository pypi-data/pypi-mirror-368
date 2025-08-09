"""
Compatibility module for ArticleSimpleVersionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_simple_version_customer.
"""

try:
    from d361api.d361api.article_simple_version_customer import ArticleSimpleVersionCustomer
    __all__ = ['ArticleSimpleVersionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleSimpleVersionCustomer = getattr(d361api, 'ArticleSimpleVersionCustomer', None)
        if ArticleSimpleVersionCustomer is None:
            raise ImportError(f"Could not find ArticleSimpleVersionCustomer in d361api module")
        __all__ = ['ArticleSimpleVersionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleSimpleVersionCustomer: {e}", ImportWarning)
        __all__ = []
