"""
Compatibility module for ContentRoleSummaryCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.content_role_summary_customer.
"""

try:
    from d361api.d361api.content_role_summary_customer import ContentRoleSummaryCustomer
    __all__ = ['ContentRoleSummaryCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ContentRoleSummaryCustomer = getattr(d361api, 'ContentRoleSummaryCustomer', None)
        if ContentRoleSummaryCustomer is None:
            raise ImportError(f"Could not find ContentRoleSummaryCustomer in d361api module")
        __all__ = ['ContentRoleSummaryCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ContentRoleSummaryCustomer: {e}", ImportWarning)
        __all__ = []
