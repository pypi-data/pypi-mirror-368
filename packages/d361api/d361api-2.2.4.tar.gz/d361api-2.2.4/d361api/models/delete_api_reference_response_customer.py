"""
Compatibility module for DeleteApiReferenceResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.delete_api_reference_response_customer.
"""

try:
    from d361api.d361api.delete_api_reference_response_customer import DeleteApiReferenceResponseCustomer
    __all__ = ['DeleteApiReferenceResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DeleteApiReferenceResponseCustomer = getattr(d361api, 'DeleteApiReferenceResponseCustomer', None)
        if DeleteApiReferenceResponseCustomer is None:
            raise ImportError(f"Could not find DeleteApiReferenceResponseCustomer in d361api module")
        __all__ = ['DeleteApiReferenceResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DeleteApiReferenceResponseCustomer: {e}", ImportWarning)
        __all__ = []
