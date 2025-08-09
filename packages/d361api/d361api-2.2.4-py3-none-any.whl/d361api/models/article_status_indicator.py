"""
Compatibility module for ArticleStatusIndicator.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.article_status_indicator.
"""

try:
    from d361api.d361api.article_status_indicator import ArticleStatusIndicator
    __all__ = ['ArticleStatusIndicator']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ArticleStatusIndicator = getattr(d361api, 'ArticleStatusIndicator', None)
        if ArticleStatusIndicator is None:
            raise ImportError(f"Could not find ArticleStatusIndicator in d361api module")
        __all__ = ['ArticleStatusIndicator']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ArticleStatusIndicator: {e}", ImportWarning)
        __all__ = []
