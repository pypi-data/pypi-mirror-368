"""
Compatibility module for AIAdditionalFeedbackInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.ai_additional_feedback_info.
"""

try:
    from d361api.d361api.ai_additional_feedback_info import AIAdditionalFeedbackInfo
    __all__ = ['AIAdditionalFeedbackInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AIAdditionalFeedbackInfo = getattr(d361api, 'AIAdditionalFeedbackInfo', None)
        if AIAdditionalFeedbackInfo is None:
            raise ImportError(f"Could not find AIAdditionalFeedbackInfo in d361api module")
        __all__ = ['AIAdditionalFeedbackInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AIAdditionalFeedbackInfo: {e}", ImportWarning)
        __all__ = []
