"""
Compatibility module for ArticleMatchedData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_matched_data.
"""

try:
    from d361api.d361api.article_matched_data import ArticleMatchedData
    __all__ = ['ArticleMatchedData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleMatchedData = getattr(d361api, 'ArticleMatchedData', None)
        if ArticleMatchedData is None:
            raise ImportError(f"Could not find ArticleMatchedData in d361api module")
        __all__ = ['ArticleMatchedData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleMatchedData: {e}", ImportWarning)
        __all__ = []
