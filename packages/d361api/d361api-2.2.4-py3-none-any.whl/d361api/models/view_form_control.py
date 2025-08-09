"""
Compatibility module for ViewFormControl.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.view_form_control.
"""

try:
    from d361api.d361api.view_form_control import ViewFormControl
    __all__ = ['ViewFormControl']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ViewFormControl = getattr(d361api, 'ViewFormControl', None)
        if ViewFormControl is None:
            raise ImportError(f"Could not find ViewFormControl in d361api module")
        __all__ = ['ViewFormControl']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ViewFormControl: {e}", ImportWarning)
        __all__ = []
