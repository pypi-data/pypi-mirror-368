"""
Compatibility module for DriveTaskStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.drive_task_status.
"""

try:
    from d361api.d361api.drive_task_status import DriveTaskStatus
    __all__ = ['DriveTaskStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DriveTaskStatus = getattr(d361api, 'DriveTaskStatus', None)
        if DriveTaskStatus is None:
            raise ImportError(f"Could not find DriveTaskStatus in d361api module")
        __all__ = ['DriveTaskStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DriveTaskStatus: {e}", ImportWarning)
        __all__ = []
