"""
Compatibility module for CategorySimpleVersionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_simple_version_customer.
"""

try:
    from d361api.d361api.category_simple_version_customer import CategorySimpleVersionCustomer
    __all__ = ['CategorySimpleVersionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategorySimpleVersionCustomer = getattr(d361api, 'CategorySimpleVersionCustomer', None)
        if CategorySimpleVersionCustomer is None:
            raise ImportError(f"Could not find CategorySimpleVersionCustomer in d361api module")
        __all__ = ['CategorySimpleVersionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategorySimpleVersionCustomer: {e}", ImportWarning)
        __all__ = []
