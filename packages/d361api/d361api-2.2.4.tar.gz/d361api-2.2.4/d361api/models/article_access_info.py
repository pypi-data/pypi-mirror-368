"""
Compatibility module for ArticleAccessInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_access_info.
"""

try:
    from d361api.d361api.article_access_info import ArticleAccessInfo
    __all__ = ['ArticleAccessInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleAccessInfo = getattr(d361api, 'ArticleAccessInfo', None)
        if ArticleAccessInfo is None:
            raise ImportError(f"Could not find ArticleAccessInfo in d361api module")
        __all__ = ['ArticleAccessInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleAccessInfo: {e}", ImportWarning)
        __all__ = []
