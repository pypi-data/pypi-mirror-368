"""
Compatibility module for ArticleUpdateWorkflowRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_update_workflow_request.
"""

try:
    from d361api.d361api.article_update_workflow_request import ArticleUpdateWorkflowRequest
    __all__ = ['ArticleUpdateWorkflowRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleUpdateWorkflowRequest = getattr(d361api, 'ArticleUpdateWorkflowRequest', None)
        if ArticleUpdateWorkflowRequest is None:
            raise ImportError(f"Could not find ArticleUpdateWorkflowRequest in d361api module")
        __all__ = ['ArticleUpdateWorkflowRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleUpdateWorkflowRequest: {e}", ImportWarning)
        __all__ = []
