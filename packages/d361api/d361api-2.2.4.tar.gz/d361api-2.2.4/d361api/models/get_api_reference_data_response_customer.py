"""
Compatibility module for GetApiReferenceDataResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_api_reference_data_response_customer.
"""

try:
    from d361api.d361api.get_api_reference_data_response_customer import GetApiReferenceDataResponseCustomer
    __all__ = ['GetApiReferenceDataResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetApiReferenceDataResponseCustomer = getattr(d361api, 'GetApiReferenceDataResponseCustomer', None)
        if GetApiReferenceDataResponseCustomer is None:
            raise ImportError(f"Could not find GetApiReferenceDataResponseCustomer in d361api module")
        __all__ = ['GetApiReferenceDataResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetApiReferenceDataResponseCustomer: {e}", ImportWarning)
        __all__ = []
