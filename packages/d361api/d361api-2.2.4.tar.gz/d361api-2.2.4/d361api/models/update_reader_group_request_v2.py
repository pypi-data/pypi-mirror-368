"""
Compatibility module for UpdateReaderGroupRequestV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_reader_group_request_v2.
"""

try:
    from d361api.d361api.update_reader_group_request_v2 import UpdateReaderGroupRequestV2
    __all__ = ['UpdateReaderGroupRequestV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateReaderGroupRequestV2 = getattr(d361api, 'UpdateReaderGroupRequestV2', None)
        if UpdateReaderGroupRequestV2 is None:
            raise ImportError(f"Could not find UpdateReaderGroupRequestV2 in d361api module")
        __all__ = ['UpdateReaderGroupRequestV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateReaderGroupRequestV2: {e}", ImportWarning)
        __all__ = []
