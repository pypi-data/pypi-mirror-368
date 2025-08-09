"""
Compatibility module for AddReaderGroupRequestV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_reader_group_request_v2.
"""

try:
    from d361api.d361api.add_reader_group_request_v2 import AddReaderGroupRequestV2
    __all__ = ['AddReaderGroupRequestV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddReaderGroupRequestV2 = getattr(d361api, 'AddReaderGroupRequestV2', None)
        if AddReaderGroupRequestV2 is None:
            raise ImportError(f"Could not find AddReaderGroupRequestV2 in d361api module")
        __all__ = ['AddReaderGroupRequestV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddReaderGroupRequestV2: {e}", ImportWarning)
        __all__ = []
