"""
Compatibility module for RoleMetaDataListCustomerApiResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.role_meta_data_list_customer_api_response.
"""

try:
    from d361api.d361api.role_meta_data_list_customer_api_response import RoleMetaDataListCustomerApiResponse
    __all__ = ['RoleMetaDataListCustomerApiResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        RoleMetaDataListCustomerApiResponse = getattr(d361api, 'RoleMetaDataListCustomerApiResponse', None)
        if RoleMetaDataListCustomerApiResponse is None:
            raise ImportError(f"Could not find RoleMetaDataListCustomerApiResponse in d361api module")
        __all__ = ['RoleMetaDataListCustomerApiResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import RoleMetaDataListCustomerApiResponse: {e}", ImportWarning)
        __all__ = []
