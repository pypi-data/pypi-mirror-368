"""
Compatibility module for AddUserData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_user_data.
"""

try:
    from d361api.d361api.add_user_data import AddUserData
    __all__ = ['AddUserData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddUserData = getattr(d361api, 'AddUserData', None)
        if AddUserData is None:
            raise ImportError(f"Could not find AddUserData in d361api module")
        __all__ = ['AddUserData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddUserData: {e}", ImportWarning)
        __all__ = []
