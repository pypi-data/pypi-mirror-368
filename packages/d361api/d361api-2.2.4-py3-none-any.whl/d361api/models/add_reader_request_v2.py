"""
Compatibility module for AddReaderRequestV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_reader_request_v2.
"""

try:
    from d361api.d361api.add_reader_request_v2 import AddReaderRequestV2
    __all__ = ['AddReaderRequestV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddReaderRequestV2 = getattr(d361api, 'AddReaderRequestV2', None)
        if AddReaderRequestV2 is None:
            raise ImportError(f"Could not find AddReaderRequestV2 in d361api module")
        __all__ = ['AddReaderRequestV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddReaderRequestV2: {e}", ImportWarning)
        __all__ = []
