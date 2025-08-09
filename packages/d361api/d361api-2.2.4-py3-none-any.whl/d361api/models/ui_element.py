"""
Compatibility module for UIElement.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.ui_element.
"""

try:
    from d361api.d361api.ui_element import UIElement
    __all__ = ['UIElement']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UIElement = getattr(d361api, 'UIElement', None)
        if UIElement is None:
            raise ImportError(f"Could not find UIElement in d361api module")
        __all__ = ['UIElement']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UIElement: {e}", ImportWarning)
        __all__ = []
