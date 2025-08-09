"""
Compatibility module for DeleteMediaFileResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.delete_media_file_response_customer.
"""

try:
    from d361api.d361api.delete_media_file_response_customer import DeleteMediaFileResponseCustomer
    __all__ = ['DeleteMediaFileResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DeleteMediaFileResponseCustomer = getattr(d361api, 'DeleteMediaFileResponseCustomer', None)
        if DeleteMediaFileResponseCustomer is None:
            raise ImportError(f"Could not find DeleteMediaFileResponseCustomer in d361api module")
        __all__ = ['DeleteMediaFileResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DeleteMediaFileResponseCustomer: {e}", ImportWarning)
        __all__ = []
