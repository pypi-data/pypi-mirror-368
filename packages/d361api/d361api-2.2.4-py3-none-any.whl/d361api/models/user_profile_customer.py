"""
Compatibility module for UserProfileCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.user_profile_customer.
"""

try:
    from d361api.d361api.user_profile_customer import UserProfileCustomer
    __all__ = ['UserProfileCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UserProfileCustomer = getattr(d361api, 'UserProfileCustomer', None)
        if UserProfileCustomer is None:
            raise ImportError(f"Could not find UserProfileCustomer in d361api module")
        __all__ = ['UserProfileCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UserProfileCustomer: {e}", ImportWarning)
        __all__ = []
