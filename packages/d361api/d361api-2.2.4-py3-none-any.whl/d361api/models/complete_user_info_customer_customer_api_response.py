"""
Compatibility module for CompleteUserInfoCustomerCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.complete_user_info_customer_customer_api_response.
"""

try:
    from d361api.d361api.complete_user_info_customer_customer_api_response import CompleteUserInfoCustomerCustomerApiResponse
    __all__ = ['CompleteUserInfoCustomerCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CompleteUserInfoCustomerCustomerApiResponse = getattr(d361api, 'CompleteUserInfoCustomerCustomerApiResponse', None)
        if CompleteUserInfoCustomerCustomerApiResponse is None:
            raise ImportError(f"Could not find CompleteUserInfoCustomerCustomerApiResponse in d361api module")
        __all__ = ['CompleteUserInfoCustomerCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CompleteUserInfoCustomerCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
