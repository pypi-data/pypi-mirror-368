"""
Compatibility module for ApiReferencePublishRequestCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_reference_publish_request_customer.
"""

try:
    from d361api.d361api.api_reference_publish_request_customer import ApiReferencePublishRequestCustomer
    __all__ = ['ApiReferencePublishRequestCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiReferencePublishRequestCustomer = getattr(d361api, 'ApiReferencePublishRequestCustomer', None)
        if ApiReferencePublishRequestCustomer is None:
            raise ImportError(f"Could not find ApiReferencePublishRequestCustomer in d361api module")
        __all__ = ['ApiReferencePublishRequestCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiReferencePublishRequestCustomer: {e}", ImportWarning)
        __all__ = []
