"""
Compatibility module for BulkArticleResultCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_article_result_customer.
"""

try:
    from d361api.d361api.bulk_article_result_customer import BulkArticleResultCustomer
    __all__ = ['BulkArticleResultCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkArticleResultCustomer = getattr(d361api, 'BulkArticleResultCustomer', None)
        if BulkArticleResultCustomer is None:
            raise ImportError(f"Could not find BulkArticleResultCustomer in d361api module")
        __all__ = ['BulkArticleResultCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkArticleResultCustomer: {e}", ImportWarning)
        __all__ = []
