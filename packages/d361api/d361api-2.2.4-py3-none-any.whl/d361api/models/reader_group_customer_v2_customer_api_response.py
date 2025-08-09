"""
Compatibility module for ReaderGroupCustomerV2CustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.reader_group_customer_v2_customer_api_response.
"""

try:
    from d361api.d361api.reader_group_customer_v2_customer_api_response import ReaderGroupCustomerV2CustomerApiResponse
    __all__ = ['ReaderGroupCustomerV2CustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ReaderGroupCustomerV2CustomerApiResponse = getattr(d361api, 'ReaderGroupCustomerV2CustomerApiResponse', None)
        if ReaderGroupCustomerV2CustomerApiResponse is None:
            raise ImportError(f"Could not find ReaderGroupCustomerV2CustomerApiResponse in d361api module")
        __all__ = ['ReaderGroupCustomerV2CustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ReaderGroupCustomerV2CustomerApiResponse: {e}", ImportWarning)
        __all__ = []
