"""
Compatibility module for ApiDocsImportDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_docs_import_data_customer.
"""

try:
    from d361api.d361api.api_docs_import_data_customer import ApiDocsImportDataCustomer
    __all__ = ['ApiDocsImportDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiDocsImportDataCustomer = getattr(d361api, 'ApiDocsImportDataCustomer', None)
        if ApiDocsImportDataCustomer is None:
            raise ImportError(f"Could not find ApiDocsImportDataCustomer in d361api module")
        __all__ = ['ApiDocsImportDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiDocsImportDataCustomer: {e}", ImportWarning)
        __all__ = []
