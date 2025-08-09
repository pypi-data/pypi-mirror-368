"""
Compatibility module for ReaderGroupCustomerV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.reader_group_customer_v2.
"""

try:
    from d361api.d361api.reader_group_customer_v2 import ReaderGroupCustomerV2
    __all__ = ['ReaderGroupCustomerV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ReaderGroupCustomerV2 = getattr(d361api, 'ReaderGroupCustomerV2', None)
        if ReaderGroupCustomerV2 is None:
            raise ImportError(f"Could not find ReaderGroupCustomerV2 in d361api module")
        __all__ = ['ReaderGroupCustomerV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ReaderGroupCustomerV2: {e}", ImportWarning)
        __all__ = []
