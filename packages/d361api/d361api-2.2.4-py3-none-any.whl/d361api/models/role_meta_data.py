"""
Compatibility module for RoleMetaData.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.role_meta_data.
"""

try:
    from d361api.d361api.role_meta_data import RoleMetaData
    __all__ = ['RoleMetaData']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        RoleMetaData = getattr(d361api, 'RoleMetaData', None)
        if RoleMetaData is None:
            raise ImportError(f"Could not find RoleMetaData in d361api module")
        __all__ = ['RoleMetaData']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import RoleMetaData: {e}", ImportWarning)
        __all__ = []
