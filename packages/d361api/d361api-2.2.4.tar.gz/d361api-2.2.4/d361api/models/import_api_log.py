"""
Compatibility module for ImportAPILog.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.import_api_log.
"""

try:
    from d361api.d361api.import_api_log import ImportAPILog
    __all__ = ['ImportAPILog']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ImportAPILog = getattr(d361api, 'ImportAPILog', None)
        if ImportAPILog is None:
            raise ImportError(f"Could not find ImportAPILog in d361api module")
        __all__ = ['ImportAPILog']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ImportAPILog: {e}", ImportWarning)
        __all__ = []
