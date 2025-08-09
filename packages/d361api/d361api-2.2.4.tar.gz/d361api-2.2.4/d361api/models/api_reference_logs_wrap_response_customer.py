"""
Compatibility module for ApiReferenceLogsWrapResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_reference_logs_wrap_response_customer.
"""

try:
    from d361api.d361api.api_reference_logs_wrap_response_customer import ApiReferenceLogsWrapResponseCustomer
    __all__ = ['ApiReferenceLogsWrapResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiReferenceLogsWrapResponseCustomer = getattr(d361api, 'ApiReferenceLogsWrapResponseCustomer', None)
        if ApiReferenceLogsWrapResponseCustomer is None:
            raise ImportError(f"Could not find ApiReferenceLogsWrapResponseCustomer in d361api module")
        __all__ = ['ApiReferenceLogsWrapResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiReferenceLogsWrapResponseCustomer: {e}", ImportWarning)
        __all__ = []
