"""
Compatibility module for LanguageMeta.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language_meta.
"""

try:
    from d361api.d361api.language_meta import LanguageMeta
    __all__ = ['LanguageMeta']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        LanguageMeta = getattr(d361api, 'LanguageMeta', None)
        if LanguageMeta is None:
            raise ImportError(f"Could not find LanguageMeta in d361api module")
        __all__ = ['LanguageMeta']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import LanguageMeta: {e}", ImportWarning)
        __all__ = []
