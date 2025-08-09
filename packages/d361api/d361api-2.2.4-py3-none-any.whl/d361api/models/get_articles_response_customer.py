"""
Compatibility module for GetArticlesResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_articles_response_customer.
"""

try:
    from d361api.d361api.get_articles_response_customer import GetArticlesResponseCustomer
    __all__ = ['GetArticlesResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetArticlesResponseCustomer = getattr(d361api, 'GetArticlesResponseCustomer', None)
        if GetArticlesResponseCustomer is None:
            raise ImportError(f"Could not find GetArticlesResponseCustomer in d361api module")
        __all__ = ['GetArticlesResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetArticlesResponseCustomer: {e}", ImportWarning)
        __all__ = []
