"""
Compatibility module for AIAssistiveSearch.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.ai_assistive_search.
"""

try:
    from d361api.d361api.ai_assistive_search import AIAssistiveSearch
    __all__ = ['AIAssistiveSearch']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AIAssistiveSearch = getattr(d361api, 'AIAssistiveSearch', None)
        if AIAssistiveSearch is None:
            raise ImportError(f"Could not find AIAssistiveSearch in d361api module")
        __all__ = ['AIAssistiveSearch']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AIAssistiveSearch: {e}", ImportWarning)
        __all__ = []
