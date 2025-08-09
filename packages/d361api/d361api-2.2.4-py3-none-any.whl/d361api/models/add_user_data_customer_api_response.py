"""
Compatibility module for AddUserDataCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_user_data_customer_api_response.
"""

try:
    from d361api.d361api.add_user_data_customer_api_response import AddUserDataCustomerApiResponse
    __all__ = ['AddUserDataCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddUserDataCustomerApiResponse = getattr(d361api, 'AddUserDataCustomerApiResponse', None)
        if AddUserDataCustomerApiResponse is None:
            raise ImportError(f"Could not find AddUserDataCustomerApiResponse in d361api module")
        __all__ = ['AddUserDataCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddUserDataCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
