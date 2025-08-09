"""
Compatibility module for DateRange.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.date_range.
"""

try:
    from d361api.d361api.date_range import DateRange
    __all__ = ['DateRange']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DateRange = getattr(d361api, 'DateRange', None)
        if DateRange is None:
            raise ImportError(f"Could not find DateRange in d361api module")
        __all__ = ['DateRange']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DateRange: {e}", ImportWarning)
        __all__ = []
