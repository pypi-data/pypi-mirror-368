"""
Compatibility module for CustomerApiBaseResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.customer_api_base_response.
"""

try:
    from d361api.d361api.customer_api_base_response import CustomerApiBaseResponse
    __all__ = ['CustomerApiBaseResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CustomerApiBaseResponse = getattr(d361api, 'CustomerApiBaseResponse', None)
        if CustomerApiBaseResponse is None:
            raise ImportError(f"Could not find CustomerApiBaseResponse in d361api module")
        __all__ = ['CustomerApiBaseResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CustomerApiBaseResponse: {e}", ImportWarning)
        __all__ = []
