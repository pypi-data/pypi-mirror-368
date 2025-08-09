"""
Compatibility module for SearchProjectVersionResponseCustomerApi.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.search_project_version_response_customer_api.
"""

try:
    from d361api.d361api.search_project_version_response_customer_api import SearchProjectVersionResponseCustomerApi
    __all__ = ['SearchProjectVersionResponseCustomerApi']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        SearchProjectVersionResponseCustomerApi = getattr(d361api, 'SearchProjectVersionResponseCustomerApi', None)
        if SearchProjectVersionResponseCustomerApi is None:
            raise ImportError(f"Could not find SearchProjectVersionResponseCustomerApi in d361api module")
        __all__ = ['SearchProjectVersionResponseCustomerApi']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import SearchProjectVersionResponseCustomerApi: {e}", ImportWarning)
        __all__ = []
