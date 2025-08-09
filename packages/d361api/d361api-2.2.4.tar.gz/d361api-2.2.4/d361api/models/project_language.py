"""
Compatibility module for ProjectLanguage.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.project_language.
"""

try:
    from d361api.d361api.project_language import ProjectLanguage
    __all__ = ['ProjectLanguage']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ProjectLanguage = getattr(d361api, 'ProjectLanguage', None)
        if ProjectLanguage is None:
            raise ImportError(f"Could not find ProjectLanguage in d361api module")
        __all__ = ['ProjectLanguage']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ProjectLanguage: {e}", ImportWarning)
        __all__ = []
