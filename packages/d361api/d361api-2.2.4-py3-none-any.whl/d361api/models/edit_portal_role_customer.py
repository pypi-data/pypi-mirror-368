"""
Compatibility module for EditPortalRoleCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.edit_portal_role_customer.
"""

try:
    from d361api.d361api.edit_portal_role_customer import EditPortalRoleCustomer
    __all__ = ['EditPortalRoleCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EditPortalRoleCustomer = getattr(d361api, 'EditPortalRoleCustomer', None)
        if EditPortalRoleCustomer is None:
            raise ImportError(f"Could not find EditPortalRoleCustomer in d361api module")
        __all__ = ['EditPortalRoleCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EditPortalRoleCustomer: {e}", ImportWarning)
        __all__ = []
