"""
Compatibility module for ApiDocumentationImportResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_documentation_import_response_customer.
"""

try:
    from d361api.d361api.api_documentation_import_response_customer import ApiDocumentationImportResponseCustomer
    __all__ = ['ApiDocumentationImportResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiDocumentationImportResponseCustomer = getattr(d361api, 'ApiDocumentationImportResponseCustomer', None)
        if ApiDocumentationImportResponseCustomer is None:
            raise ImportError(f"Could not find ApiDocumentationImportResponseCustomer in d361api module")
        __all__ = ['ApiDocumentationImportResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiDocumentationImportResponseCustomer: {e}", ImportWarning)
        __all__ = []
