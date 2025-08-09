"""
Compatibility module for CategoryWorkflowStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_workflow_status.
"""

try:
    from d361api.d361api.category_workflow_status import CategoryWorkflowStatus
    __all__ = ['CategoryWorkflowStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategoryWorkflowStatus = getattr(d361api, 'CategoryWorkflowStatus', None)
        if CategoryWorkflowStatus is None:
            raise ImportError(f"Could not find CategoryWorkflowStatus in d361api module")
        __all__ = ['CategoryWorkflowStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategoryWorkflowStatus: {e}", ImportWarning)
        __all__ = []
