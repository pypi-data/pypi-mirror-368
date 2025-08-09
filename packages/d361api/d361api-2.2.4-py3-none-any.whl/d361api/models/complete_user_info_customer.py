"""
Compatibility module for CompleteUserInfoCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.complete_user_info_customer.
"""

try:
    from d361api.d361api.complete_user_info_customer import CompleteUserInfoCustomer
    __all__ = ['CompleteUserInfoCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CompleteUserInfoCustomer = getattr(d361api, 'CompleteUserInfoCustomer', None)
        if CompleteUserInfoCustomer is None:
            raise ImportError(f"Could not find CompleteUserInfoCustomer in d361api module")
        __all__ = ['CompleteUserInfoCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CompleteUserInfoCustomer: {e}", ImportWarning)
        __all__ = []
