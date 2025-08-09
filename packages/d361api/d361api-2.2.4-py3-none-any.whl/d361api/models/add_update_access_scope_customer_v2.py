"""
Compatibility module for AddUpdateAccessScopeCustomerV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_update_access_scope_customer_v2.
"""

try:
    from d361api.d361api.add_update_access_scope_customer_v2 import AddUpdateAccessScopeCustomerV2
    __all__ = ['AddUpdateAccessScopeCustomerV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddUpdateAccessScopeCustomerV2 = getattr(d361api, 'AddUpdateAccessScopeCustomerV2', None)
        if AddUpdateAccessScopeCustomerV2 is None:
            raise ImportError(f"Could not find AddUpdateAccessScopeCustomerV2 in d361api module")
        __all__ = ['AddUpdateAccessScopeCustomerV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddUpdateAccessScopeCustomerV2: {e}", ImportWarning)
        __all__ = []
