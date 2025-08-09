"""
Compatibility module for BulkDeleteArticleVersionResonse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.bulk_delete_article_version_resonse.
"""

try:
    from d361api.d361api.bulk_delete_article_version_resonse import BulkDeleteArticleVersionResonse
    __all__ = ['BulkDeleteArticleVersionResonse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BulkDeleteArticleVersionResonse = getattr(d361api, 'BulkDeleteArticleVersionResonse', None)
        if BulkDeleteArticleVersionResonse is None:
            raise ImportError(f"Could not find BulkDeleteArticleVersionResonse in d361api module")
        __all__ = ['BulkDeleteArticleVersionResonse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BulkDeleteArticleVersionResonse: {e}", ImportWarning)
        __all__ = []
