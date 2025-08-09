"""
Compatibility module for ApiLogs.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_logs.
"""

try:
    from d361api.d361api.api_logs import ApiLogs
    __all__ = ['ApiLogs']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiLogs = getattr(d361api, 'ApiLogs', None)
        if ApiLogs is None:
            raise ImportError(f"Could not find ApiLogs in d361api module")
        __all__ = ['ApiLogs']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiLogs: {e}", ImportWarning)
        __all__ = []
