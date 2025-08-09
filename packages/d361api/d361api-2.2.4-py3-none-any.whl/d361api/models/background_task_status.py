"""
Compatibility module for BackgroundTaskStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.background_task_status.
"""

try:
    from d361api.d361api.background_task_status import BackgroundTaskStatus
    __all__ = ['BackgroundTaskStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BackgroundTaskStatus = getattr(d361api, 'BackgroundTaskStatus', None)
        if BackgroundTaskStatus is None:
            raise ImportError(f"Could not find BackgroundTaskStatus in d361api module")
        __all__ = ['BackgroundTaskStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BackgroundTaskStatus: {e}", ImportWarning)
        __all__ = []
