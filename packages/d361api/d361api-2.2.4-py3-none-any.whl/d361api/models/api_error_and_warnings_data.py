"""
Compatibility module for ApiErrorAndWarningsData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_error_and_warnings_data.
"""

try:
    from d361api.d361api.api_error_and_warnings_data import ApiErrorAndWarningsData
    __all__ = ['ApiErrorAndWarningsData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiErrorAndWarningsData = getattr(d361api, 'ApiErrorAndWarningsData', None)
        if ApiErrorAndWarningsData is None:
            raise ImportError(f"Could not find ApiErrorAndWarningsData in d361api module")
        __all__ = ['ApiErrorAndWarningsData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiErrorAndWarningsData: {e}", ImportWarning)
        __all__ = []
