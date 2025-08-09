"""
Compatibility module for LanguageAccessInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language_access_info.
"""

try:
    from d361api.d361api.language_access_info import LanguageAccessInfo
    __all__ = ['LanguageAccessInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        LanguageAccessInfo = getattr(d361api, 'LanguageAccessInfo', None)
        if LanguageAccessInfo is None:
            raise ImportError(f"Could not find LanguageAccessInfo in d361api module")
        __all__ = ['LanguageAccessInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import LanguageAccessInfo: {e}", ImportWarning)
        __all__ = []
