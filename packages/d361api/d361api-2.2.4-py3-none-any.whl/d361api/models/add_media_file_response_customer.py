"""
Compatibility module for AddMediaFileResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_media_file_response_customer.
"""

try:
    from d361api.d361api.add_media_file_response_customer import AddMediaFileResponseCustomer
    __all__ = ['AddMediaFileResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddMediaFileResponseCustomer = getattr(d361api, 'AddMediaFileResponseCustomer', None)
        if AddMediaFileResponseCustomer is None:
            raise ImportError(f"Could not find AddMediaFileResponseCustomer in d361api module")
        __all__ = ['AddMediaFileResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddMediaFileResponseCustomer: {e}", ImportWarning)
        __all__ = []
