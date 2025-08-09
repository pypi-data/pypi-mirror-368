"""
Compatibility module for AIAssistiveSearchRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.ai_assistive_search_request.
"""

try:
    from d361api.d361api.ai_assistive_search_request import AIAssistiveSearchRequest
    __all__ = ['AIAssistiveSearchRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AIAssistiveSearchRequest = getattr(d361api, 'AIAssistiveSearchRequest', None)
        if AIAssistiveSearchRequest is None:
            raise ImportError(f"Could not find AIAssistiveSearchRequest in d361api module")
        __all__ = ['AIAssistiveSearchRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AIAssistiveSearchRequest: {e}", ImportWarning)
        __all__ = []
