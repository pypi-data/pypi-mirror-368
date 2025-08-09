"""
Compatibility module for UserDetailsCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.user_details_customer.
"""

try:
    from d361api.d361api.user_details_customer import UserDetailsCustomer
    __all__ = ['UserDetailsCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UserDetailsCustomer = getattr(d361api, 'UserDetailsCustomer', None)
        if UserDetailsCustomer is None:
            raise ImportError(f"Could not find UserDetailsCustomer in d361api module")
        __all__ = ['UserDetailsCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UserDetailsCustomer: {e}", ImportWarning)
        __all__ = []
