"""
Compatibility module for RoleSummaryCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.role_summary_customer.
"""

try:
    from d361api.d361api.role_summary_customer import RoleSummaryCustomer
    __all__ = ['RoleSummaryCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        RoleSummaryCustomer = getattr(d361api, 'RoleSummaryCustomer', None)
        if RoleSummaryCustomer is None:
            raise ImportError(f"Could not find RoleSummaryCustomer in d361api module")
        __all__ = ['RoleSummaryCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import RoleSummaryCustomer: {e}", ImportWarning)
        __all__ = []
