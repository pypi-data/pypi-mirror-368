"""
Compatibility module for PublicAPIAIFeedbackRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.public_apiai_feedback_request.
"""

try:
    from d361api.d361api.public_apiai_feedback_request import PublicAPIAIFeedbackRequest
    __all__ = ['PublicAPIAIFeedbackRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        PublicAPIAIFeedbackRequest = getattr(d361api, 'PublicAPIAIFeedbackRequest', None)
        if PublicAPIAIFeedbackRequest is None:
            raise ImportError(f"Could not find PublicAPIAIFeedbackRequest in d361api module")
        __all__ = ['PublicAPIAIFeedbackRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import PublicAPIAIFeedbackRequest: {e}", ImportWarning)
        __all__ = []
