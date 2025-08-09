"""
Compatibility module for RelatedArticleData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.related_article_data.
"""

try:
    from d361api.d361api.related_article_data import RelatedArticleData
    __all__ = ['RelatedArticleData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        RelatedArticleData = getattr(d361api, 'RelatedArticleData', None)
        if RelatedArticleData is None:
            raise ImportError(f"Could not find RelatedArticleData in d361api module")
        __all__ = ['RelatedArticleData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import RelatedArticleData: {e}", ImportWarning)
        __all__ = []
