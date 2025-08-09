"""
Compatibility module for BooleanCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.boolean_customer_api_response.
"""

try:
    from d361api.d361api.boolean_customer_api_response import BooleanCustomerApiResponse
    __all__ = ['BooleanCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BooleanCustomerApiResponse = getattr(d361api, 'BooleanCustomerApiResponse', None)
        if BooleanCustomerApiResponse is None:
            raise ImportError(f"Could not find BooleanCustomerApiResponse in d361api module")
        __all__ = ['BooleanCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BooleanCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
