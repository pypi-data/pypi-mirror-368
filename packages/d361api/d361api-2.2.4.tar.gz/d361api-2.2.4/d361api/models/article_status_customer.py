"""
Compatibility module for ArticleStatusCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_status_customer.
"""

try:
    from d361api.d361api.article_status_customer import ArticleStatusCustomer
    __all__ = ['ArticleStatusCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleStatusCustomer = getattr(d361api, 'ArticleStatusCustomer', None)
        if ArticleStatusCustomer is None:
            raise ImportError(f"Could not find ArticleStatusCustomer in d361api module")
        __all__ = ['ArticleStatusCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleStatusCustomer: {e}", ImportWarning)
        __all__ = []
