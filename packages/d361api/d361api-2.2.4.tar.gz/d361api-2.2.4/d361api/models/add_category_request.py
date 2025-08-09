"""
Compatibility module for AddCategoryRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_category_request.
"""

try:
    from d361api.d361api.add_category_request import AddCategoryRequest
    __all__ = ['AddCategoryRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddCategoryRequest = getattr(d361api, 'AddCategoryRequest', None)
        if AddCategoryRequest is None:
            raise ImportError(f"Could not find AddCategoryRequest in d361api module")
        __all__ = ['AddCategoryRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddCategoryRequest: {e}", ImportWarning)
        __all__ = []
