"""
Compatibility module for MediaFileDataResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_file_data_response_customer.
"""

try:
    from d361api.d361api.media_file_data_response_customer import MediaFileDataResponseCustomer
    __all__ = ['MediaFileDataResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFileDataResponseCustomer = getattr(d361api, 'MediaFileDataResponseCustomer', None)
        if MediaFileDataResponseCustomer is None:
            raise ImportError(f"Could not find MediaFileDataResponseCustomer in d361api module")
        __all__ = ['MediaFileDataResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFileDataResponseCustomer: {e}", ImportWarning)
        __all__ = []
