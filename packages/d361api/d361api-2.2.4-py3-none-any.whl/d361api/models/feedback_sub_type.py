"""
Compatibility module for FeedbackSubType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feedback_sub_type.
"""

try:
    from d361api.d361api.feedback_sub_type import FeedbackSubType
    __all__ = ['FeedbackSubType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeedbackSubType = getattr(d361api, 'FeedbackSubType', None)
        if FeedbackSubType is None:
            raise ImportError(f"Could not find FeedbackSubType in d361api module")
        __all__ = ['FeedbackSubType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeedbackSubType: {e}", ImportWarning)
        __all__ = []
