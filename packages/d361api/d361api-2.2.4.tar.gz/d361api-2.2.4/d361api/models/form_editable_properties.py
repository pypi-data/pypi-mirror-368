"""
Compatibility module for FormEditableProperties.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.form_editable_properties.
"""

try:
    from d361api.d361api.form_editable_properties import FormEditableProperties
    __all__ = ['FormEditableProperties']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FormEditableProperties = getattr(d361api, 'FormEditableProperties', None)
        if FormEditableProperties is None:
            raise ImportError(f"Could not find FormEditableProperties in d361api module")
        __all__ = ['FormEditableProperties']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FormEditableProperties: {e}", ImportWarning)
        __all__ = []
