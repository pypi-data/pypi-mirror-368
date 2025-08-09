"""
Compatibility module for ExportType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.export_type.
"""

try:
    from d361api.d361api.export_type import ExportType
    __all__ = ['ExportType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ExportType = getattr(d361api, 'ExportType', None)
        if ExportType is None:
            raise ImportError(f"Could not find ExportType in d361api module")
        __all__ = ['ExportType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ExportType: {e}", ImportWarning)
        __all__ = []
