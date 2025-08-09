"""
Compatibility module for CategorySettingsCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_settings_customer.
"""

try:
    from d361api.d361api.category_settings_customer import CategorySettingsCustomer
    __all__ = ['CategorySettingsCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategorySettingsCustomer = getattr(d361api, 'CategorySettingsCustomer', None)
        if CategorySettingsCustomer is None:
            raise ImportError(f"Could not find CategorySettingsCustomer in d361api module")
        __all__ = ['CategorySettingsCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategorySettingsCustomer: {e}", ImportWarning)
        __all__ = []
