"""
Compatibility module for GetReaderResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_reader_response_customer.
"""

try:
    from d361api.d361api.get_reader_response_customer import GetReaderResponseCustomer
    __all__ = ['GetReaderResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetReaderResponseCustomer = getattr(d361api, 'GetReaderResponseCustomer', None)
        if GetReaderResponseCustomer is None:
            raise ImportError(f"Could not find GetReaderResponseCustomer in d361api module")
        __all__ = ['GetReaderResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetReaderResponseCustomer: {e}", ImportWarning)
        __all__ = []
