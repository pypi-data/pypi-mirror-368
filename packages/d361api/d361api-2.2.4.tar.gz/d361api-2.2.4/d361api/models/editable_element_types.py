"""
Compatibility module for EditableElementTypes.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.editable_element_types.
"""

try:
    from d361api.d361api.editable_element_types import EditableElementTypes
    __all__ = ['EditableElementTypes']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EditableElementTypes = getattr(d361api, 'EditableElementTypes', None)
        if EditableElementTypes is None:
            raise ImportError(f"Could not find EditableElementTypes in d361api module")
        __all__ = ['EditableElementTypes']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EditableElementTypes: {e}", ImportWarning)
        __all__ = []
