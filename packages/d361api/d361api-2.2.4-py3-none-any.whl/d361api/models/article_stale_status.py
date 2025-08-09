"""
Compatibility module for ArticleStaleStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_stale_status.
"""

try:
    from d361api.d361api.article_stale_status import ArticleStaleStatus
    __all__ = ['ArticleStaleStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleStaleStatus = getattr(d361api, 'ArticleStaleStatus', None)
        if ArticleStaleStatus is None:
            raise ImportError(f"Could not find ArticleStaleStatus in d361api module")
        __all__ = ['ArticleStaleStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleStaleStatus: {e}", ImportWarning)
        __all__ = []
