"""
Compatibility module for ApiReferenceLogsDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_reference_logs_data_customer.
"""

try:
    from d361api.d361api.api_reference_logs_data_customer import ApiReferenceLogsDataCustomer
    __all__ = ['ApiReferenceLogsDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiReferenceLogsDataCustomer = getattr(d361api, 'ApiReferenceLogsDataCustomer', None)
        if ApiReferenceLogsDataCustomer is None:
            raise ImportError(f"Could not find ApiReferenceLogsDataCustomer in d361api module")
        __all__ = ['ApiReferenceLogsDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiReferenceLogsDataCustomer: {e}", ImportWarning)
        __all__ = []
