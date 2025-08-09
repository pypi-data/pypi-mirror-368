"""
Compatibility module for GetArticleResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_article_response_customer.
"""

try:
    from d361api.d361api.get_article_response_customer import GetArticleResponseCustomer
    __all__ = ['GetArticleResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticleResponseCustomer = getattr(d361api, 'GetArticleResponseCustomer', None)
        if GetArticleResponseCustomer is None:
            raise ImportError(f"Could not find GetArticleResponseCustomer in d361api module")
        __all__ = ['GetArticleResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticleResponseCustomer: {e}", ImportWarning)
        __all__ = []
