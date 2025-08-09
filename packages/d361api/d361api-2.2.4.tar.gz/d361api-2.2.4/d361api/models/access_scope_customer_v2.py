"""
Compatibility module for AccessScopeCustomerV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.access_scope_customer_v2.
"""

try:
    from d361api.d361api.access_scope_customer_v2 import AccessScopeCustomerV2
    __all__ = ['AccessScopeCustomerV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AccessScopeCustomerV2 = getattr(d361api, 'AccessScopeCustomerV2', None)
        if AccessScopeCustomerV2 is None:
            raise ImportError(f"Could not find AccessScopeCustomerV2 in d361api module")
        __all__ = ['AccessScopeCustomerV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AccessScopeCustomerV2: {e}", ImportWarning)
        __all__ = []
