"""
Compatibility module for GetWorkflowStatusResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_workflow_status_response.
"""

try:
    from d361api.d361api.get_workflow_status_response import GetWorkflowStatusResponse
    __all__ = ['GetWorkflowStatusResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetWorkflowStatusResponse = getattr(d361api, 'GetWorkflowStatusResponse', None)
        if GetWorkflowStatusResponse is None:
            raise ImportError(f"Could not find GetWorkflowStatusResponse in d361api module")
        __all__ = ['GetWorkflowStatusResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetWorkflowStatusResponse: {e}", ImportWarning)
        __all__ = []
