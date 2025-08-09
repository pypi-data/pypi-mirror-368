"""
Compatibility module for ArticleWorkflowStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_workflow_status.
"""

try:
    from d361api.d361api.article_workflow_status import ArticleWorkflowStatus
    __all__ = ['ArticleWorkflowStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleWorkflowStatus = getattr(d361api, 'ArticleWorkflowStatus', None)
        if ArticleWorkflowStatus is None:
            raise ImportError(f"Could not find ArticleWorkflowStatus in d361api module")
        __all__ = ['ArticleWorkflowStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleWorkflowStatus: {e}", ImportWarning)
        __all__ = []
