"""
Compatibility module for GetLanguageFromProjectVersion.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_language_from_project_version.
"""

try:
    from d361api.d361api.get_language_from_project_version import GetLanguageFromProjectVersion
    __all__ = ['GetLanguageFromProjectVersion']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetLanguageFromProjectVersion = getattr(d361api, 'GetLanguageFromProjectVersion', None)
        if GetLanguageFromProjectVersion is None:
            raise ImportError(f"Could not find GetLanguageFromProjectVersion in d361api module")
        __all__ = ['GetLanguageFromProjectVersion']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetLanguageFromProjectVersion: {e}", ImportWarning)
        __all__ = []
