"""
Compatibility module for EditContentRoleCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.edit_content_role_customer.
"""

try:
    from d361api.d361api.edit_content_role_customer import EditContentRoleCustomer
    __all__ = ['EditContentRoleCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EditContentRoleCustomer = getattr(d361api, 'EditContentRoleCustomer', None)
        if EditContentRoleCustomer is None:
            raise ImportError(f"Could not find EditContentRoleCustomer in d361api module")
        __all__ = ['EditContentRoleCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EditContentRoleCustomer: {e}", ImportWarning)
        __all__ = []
