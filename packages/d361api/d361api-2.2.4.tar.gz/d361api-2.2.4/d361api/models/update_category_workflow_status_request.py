"""
Compatibility module for UpdateCategoryWorkflowStatusRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_category_workflow_status_request.
"""

try:
    from d361api.d361api.update_category_workflow_status_request import UpdateCategoryWorkflowStatusRequest
    __all__ = ['UpdateCategoryWorkflowStatusRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateCategoryWorkflowStatusRequest = getattr(d361api, 'UpdateCategoryWorkflowStatusRequest', None)
        if UpdateCategoryWorkflowStatusRequest is None:
            raise ImportError(f"Could not find UpdateCategoryWorkflowStatusRequest in d361api module")
        __all__ = ['UpdateCategoryWorkflowStatusRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateCategoryWorkflowStatusRequest: {e}", ImportWarning)
        __all__ = []
