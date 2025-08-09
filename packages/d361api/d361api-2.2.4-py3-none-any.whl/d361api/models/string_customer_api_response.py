"""
Compatibility module for StringCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.string_customer_api_response.
"""

try:
    from d361api.d361api.string_customer_api_response import StringCustomerApiResponse
    __all__ = ['StringCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        StringCustomerApiResponse = getattr(d361api, 'StringCustomerApiResponse', None)
        if StringCustomerApiResponse is None:
            raise ImportError(f"Could not find StringCustomerApiResponse in d361api module")
        __all__ = ['StringCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import StringCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
