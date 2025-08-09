"""
Compatibility module for ArticleContentType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_content_type.
"""

try:
    from d361api.d361api.article_content_type import ArticleContentType
    __all__ = ['ArticleContentType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleContentType = getattr(d361api, 'ArticleContentType', None)
        if ArticleContentType is None:
            raise ImportError(f"Could not find ArticleContentType in d361api module")
        __all__ = ['ArticleContentType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleContentType: {e}", ImportWarning)
        __all__ = []
