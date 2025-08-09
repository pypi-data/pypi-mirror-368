"""
Compatibility module for UpdateReaderRequestV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_reader_request_v2.
"""

try:
    from d361api.d361api.update_reader_request_v2 import UpdateReaderRequestV2
    __all__ = ['UpdateReaderRequestV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateReaderRequestV2 = getattr(d361api, 'UpdateReaderRequestV2', None)
        if UpdateReaderRequestV2 is None:
            raise ImportError(f"Could not find UpdateReaderRequestV2 in d361api module")
        __all__ = ['UpdateReaderRequestV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateReaderRequestV2: {e}", ImportWarning)
        __all__ = []
