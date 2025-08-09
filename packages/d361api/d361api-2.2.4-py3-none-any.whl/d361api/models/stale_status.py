"""
Compatibility module for StaleStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.stale_status.
"""

try:
    from d361api.d361api.stale_status import StaleStatus
    __all__ = ['StaleStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        StaleStatus = getattr(d361api, 'StaleStatus', None)
        if StaleStatus is None:
            raise ImportError(f"Could not find StaleStatus in d361api module")
        __all__ = ['StaleStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import StaleStatus: {e}", ImportWarning)
        __all__ = []
