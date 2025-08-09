"""
Compatibility module for BulkCreateArticleResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_create_article_response_customer.
"""

try:
    from d361api.d361api.bulk_create_article_response_customer import BulkCreateArticleResponseCustomer
    __all__ = ['BulkCreateArticleResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkCreateArticleResponseCustomer = getattr(d361api, 'BulkCreateArticleResponseCustomer', None)
        if BulkCreateArticleResponseCustomer is None:
            raise ImportError(f"Could not find BulkCreateArticleResponseCustomer in d361api module")
        __all__ = ['BulkCreateArticleResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkCreateArticleResponseCustomer: {e}", ImportWarning)
        __all__ = []
