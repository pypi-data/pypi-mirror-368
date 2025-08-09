"""
Compatibility module for ApiDocsResyncDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_docs_resync_data_customer.
"""

try:
    from d361api.d361api.api_docs_resync_data_customer import ApiDocsResyncDataCustomer
    __all__ = ['ApiDocsResyncDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiDocsResyncDataCustomer = getattr(d361api, 'ApiDocsResyncDataCustomer', None)
        if ApiDocsResyncDataCustomer is None:
            raise ImportError(f"Could not find ApiDocsResyncDataCustomer in d361api module")
        __all__ = ['ApiDocsResyncDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiDocsResyncDataCustomer: {e}", ImportWarning)
        __all__ = []
