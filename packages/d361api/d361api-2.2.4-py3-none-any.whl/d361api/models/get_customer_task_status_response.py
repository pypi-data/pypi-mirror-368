"""
Compatibility module for GetCustomerTaskStatusResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_customer_task_status_response.
"""

try:
    from d361api.d361api.get_customer_task_status_response import GetCustomerTaskStatusResponse
    __all__ = ['GetCustomerTaskStatusResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCustomerTaskStatusResponse = getattr(d361api, 'GetCustomerTaskStatusResponse', None)
        if GetCustomerTaskStatusResponse is None:
            raise ImportError(f"Could not find GetCustomerTaskStatusResponse in d361api module")
        __all__ = ['GetCustomerTaskStatusResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCustomerTaskStatusResponse: {e}", ImportWarning)
        __all__ = []
