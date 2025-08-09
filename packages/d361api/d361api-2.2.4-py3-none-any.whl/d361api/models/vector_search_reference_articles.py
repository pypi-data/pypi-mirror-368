"""
Compatibility module for VectorSearchReferenceArticles.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.vector_search_reference_articles.
"""

try:
    from d361api.d361api.vector_search_reference_articles import VectorSearchReferenceArticles
    __all__ = ['VectorSearchReferenceArticles']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        VectorSearchReferenceArticles = getattr(d361api, 'VectorSearchReferenceArticles', None)
        if VectorSearchReferenceArticles is None:
            raise ImportError(f"Could not find VectorSearchReferenceArticles in d361api module")
        __all__ = ['VectorSearchReferenceArticles']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import VectorSearchReferenceArticles: {e}", ImportWarning)
        __all__ = []
