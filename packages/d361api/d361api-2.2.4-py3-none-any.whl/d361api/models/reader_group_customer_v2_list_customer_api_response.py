"""
Compatibility module for ReaderGroupCustomerV2ListCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.reader_group_customer_v2_list_customer_api_response.
"""

try:
    from d361api.d361api.reader_group_customer_v2_list_customer_api_response import ReaderGroupCustomerV2ListCustomerApiResponse
    __all__ = ['ReaderGroupCustomerV2ListCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ReaderGroupCustomerV2ListCustomerApiResponse = getattr(d361api, 'ReaderGroupCustomerV2ListCustomerApiResponse', None)
        if ReaderGroupCustomerV2ListCustomerApiResponse is None:
            raise ImportError(f"Could not find ReaderGroupCustomerV2ListCustomerApiResponse in d361api module")
        __all__ = ['ReaderGroupCustomerV2ListCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ReaderGroupCustomerV2ListCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
