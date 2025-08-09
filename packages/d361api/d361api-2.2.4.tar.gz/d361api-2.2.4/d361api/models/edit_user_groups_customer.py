"""
Compatibility module for EditUserGroupsCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.edit_user_groups_customer.
"""

try:
    from d361api.d361api.edit_user_groups_customer import EditUserGroupsCustomer
    __all__ = ['EditUserGroupsCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EditUserGroupsCustomer = getattr(d361api, 'EditUserGroupsCustomer', None)
        if EditUserGroupsCustomer is None:
            raise ImportError(f"Could not find EditUserGroupsCustomer in d361api module")
        __all__ = ['EditUserGroupsCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EditUserGroupsCustomer: {e}", ImportWarning)
        __all__ = []
