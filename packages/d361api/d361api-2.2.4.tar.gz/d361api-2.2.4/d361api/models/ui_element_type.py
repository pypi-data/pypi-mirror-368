"""
Compatibility module for UIElementType.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.ui_element_type.
"""

try:
    from d361api.d361api.ui_element_type import UIElementType
    __all__ = ['UIElementType']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UIElementType = getattr(d361api, 'UIElementType', None)
        if UIElementType is None:
            raise ImportError(f"Could not find UIElementType in d361api module")
        __all__ = ['UIElementType']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UIElementType: {e}", ImportWarning)
        __all__ = []
