"""
Compatibility module for AddCategoryResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_category_response.
"""

try:
    from d361api.d361api.add_category_response import AddCategoryResponse
    __all__ = ['AddCategoryResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddCategoryResponse = getattr(d361api, 'AddCategoryResponse', None)
        if AddCategoryResponse is None:
            raise ImportError(f"Could not find AddCategoryResponse in d361api module")
        __all__ = ['AddCategoryResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddCategoryResponse: {e}", ImportWarning)
        __all__ = []
