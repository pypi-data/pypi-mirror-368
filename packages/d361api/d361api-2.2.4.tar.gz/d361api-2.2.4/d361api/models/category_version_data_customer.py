"""
Compatibility module for CategoryVersionDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_version_data_customer.
"""

try:
    from d361api.d361api.category_version_data_customer import CategoryVersionDataCustomer
    __all__ = ['CategoryVersionDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryVersionDataCustomer = getattr(d361api, 'CategoryVersionDataCustomer', None)
        if CategoryVersionDataCustomer is None:
            raise ImportError(f"Could not find CategoryVersionDataCustomer in d361api module")
        __all__ = ['CategoryVersionDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryVersionDataCustomer: {e}", ImportWarning)
        __all__ = []
