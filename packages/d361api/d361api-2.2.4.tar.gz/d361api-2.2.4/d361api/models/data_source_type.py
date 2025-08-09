"""
Compatibility module for DataSourceType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.data_source_type.
"""

try:
    from d361api.d361api.data_source_type import DataSourceType
    __all__ = ['DataSourceType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DataSourceType = getattr(d361api, 'DataSourceType', None)
        if DataSourceType is None:
            raise ImportError(f"Could not find DataSourceType in d361api module")
        __all__ = ['DataSourceType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DataSourceType: {e}", ImportWarning)
        __all__ = []
