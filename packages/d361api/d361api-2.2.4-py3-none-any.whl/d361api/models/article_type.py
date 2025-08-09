"""
Compatibility module for ArticleType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_type.
"""

try:
    from d361api.d361api.article_type import ArticleType
    __all__ = ['ArticleType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleType = getattr(d361api, 'ArticleType', None)
        if ArticleType is None:
            raise ImportError(f"Could not find ArticleType in d361api module")
        __all__ = ['ArticleType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleType: {e}", ImportWarning)
        __all__ = []
