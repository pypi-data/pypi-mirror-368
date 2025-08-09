"""
Compatibility module for CategoryDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_data_customer.
"""

try:
    from d361api.d361api.category_data_customer import CategoryDataCustomer
    __all__ = ['CategoryDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryDataCustomer = getattr(d361api, 'CategoryDataCustomer', None)
        if CategoryDataCustomer is None:
            raise ImportError(f"Could not find CategoryDataCustomer in d361api module")
        __all__ = ['CategoryDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryDataCustomer: {e}", ImportWarning)
        __all__ = []
