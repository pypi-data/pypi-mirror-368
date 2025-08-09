"""
Compatibility module for ProjectVersionTypeCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.project_version_type_customer.
"""

try:
    from d361api.d361api.project_version_type_customer import ProjectVersionTypeCustomer
    __all__ = ['ProjectVersionTypeCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ProjectVersionTypeCustomer = getattr(d361api, 'ProjectVersionTypeCustomer', None)
        if ProjectVersionTypeCustomer is None:
            raise ImportError(f"Could not find ProjectVersionTypeCustomer in d361api module")
        __all__ = ['ProjectVersionTypeCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ProjectVersionTypeCustomer: {e}", ImportWarning)
        __all__ = []
