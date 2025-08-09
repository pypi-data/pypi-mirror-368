"""
Compatibility module for Language.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language.
"""

try:
    from d361api.d361api.language import Language
    __all__ = ['Language']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Language = getattr(d361api, 'Language', None)
        if Language is None:
            raise ImportError(f"Could not find Language in d361api module")
        __all__ = ['Language']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Language: {e}", ImportWarning)
        __all__ = []
