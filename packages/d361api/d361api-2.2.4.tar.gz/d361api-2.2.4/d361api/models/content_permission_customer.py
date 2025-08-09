"""
Compatibility module for ContentPermissionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.content_permission_customer.
"""

try:
    from d361api.d361api.content_permission_customer import ContentPermissionCustomer
    __all__ = ['ContentPermissionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ContentPermissionCustomer = getattr(d361api, 'ContentPermissionCustomer', None)
        if ContentPermissionCustomer is None:
            raise ImportError(f"Could not find ContentPermissionCustomer in d361api module")
        __all__ = ['ContentPermissionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ContentPermissionCustomer: {e}", ImportWarning)
        __all__ = []
