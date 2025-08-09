"""
Compatibility module for ProjectVersionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.project_version_customer.
"""

try:
    from d361api.d361api.project_version_customer import ProjectVersionCustomer
    __all__ = ['ProjectVersionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ProjectVersionCustomer = getattr(d361api, 'ProjectVersionCustomer', None)
        if ProjectVersionCustomer is None:
            raise ImportError(f"Could not find ProjectVersionCustomer in d361api module")
        __all__ = ['ProjectVersionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ProjectVersionCustomer: {e}", ImportWarning)
        __all__ = []
