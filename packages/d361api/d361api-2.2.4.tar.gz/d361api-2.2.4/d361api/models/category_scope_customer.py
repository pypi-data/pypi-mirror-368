"""
Compatibility module for CategoryScopeCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_scope_customer.
"""

try:
    from d361api.d361api.category_scope_customer import CategoryScopeCustomer
    __all__ = ['CategoryScopeCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryScopeCustomer = getattr(d361api, 'CategoryScopeCustomer', None)
        if CategoryScopeCustomer is None:
            raise ImportError(f"Could not find CategoryScopeCustomer in d361api module")
        __all__ = ['CategoryScopeCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryScopeCustomer: {e}", ImportWarning)
        __all__ = []
