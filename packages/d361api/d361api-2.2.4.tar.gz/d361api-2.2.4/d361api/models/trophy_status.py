"""
Compatibility module for TrophyStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.trophy_status.
"""

try:
    from d361api.d361api.trophy_status import TrophyStatus
    __all__ = ['TrophyStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TrophyStatus = getattr(d361api, 'TrophyStatus', None)
        if TrophyStatus is None:
            raise ImportError(f"Could not find TrophyStatus in d361api module")
        __all__ = ['TrophyStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TrophyStatus: {e}", ImportWarning)
        __all__ = []
