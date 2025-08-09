"""
Compatibility module for ForkArticleVersionRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.fork_article_version_request.
"""

try:
    from d361api.d361api.fork_article_version_request import ForkArticleVersionRequest
    __all__ = ['ForkArticleVersionRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ForkArticleVersionRequest = getattr(d361api, 'ForkArticleVersionRequest', None)
        if ForkArticleVersionRequest is None:
            raise ImportError(f"Could not find ForkArticleVersionRequest in d361api module")
        __all__ = ['ForkArticleVersionRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ForkArticleVersionRequest: {e}", ImportWarning)
        __all__ = []
