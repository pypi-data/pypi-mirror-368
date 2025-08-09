"""
Compatibility module for WorkflowStatusCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.workflow_status_customer.
"""

try:
    from d361api.d361api.workflow_status_customer import WorkflowStatusCustomer
    __all__ = ['WorkflowStatusCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        WorkflowStatusCustomer = getattr(d361api, 'WorkflowStatusCustomer', None)
        if WorkflowStatusCustomer is None:
            raise ImportError(f"Could not find WorkflowStatusCustomer in d361api module")
        __all__ = ['WorkflowStatusCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import WorkflowStatusCustomer: {e}", ImportWarning)
        __all__ = []
