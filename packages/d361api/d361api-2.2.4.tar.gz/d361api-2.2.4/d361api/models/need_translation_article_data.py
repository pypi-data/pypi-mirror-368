"""
Compatibility module for NeedTranslationArticleData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.need_translation_article_data.
"""

try:
    from d361api.d361api.need_translation_article_data import NeedTranslationArticleData
    __all__ = ['NeedTranslationArticleData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        NeedTranslationArticleData = getattr(d361api, 'NeedTranslationArticleData', None)
        if NeedTranslationArticleData is None:
            raise ImportError(f"Could not find NeedTranslationArticleData in d361api module")
        __all__ = ['NeedTranslationArticleData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import NeedTranslationArticleData: {e}", ImportWarning)
        __all__ = []
