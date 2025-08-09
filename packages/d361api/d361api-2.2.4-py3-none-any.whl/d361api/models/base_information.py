"""
Compatibility module for BaseInformation.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.base_information.
"""

try:
    from d361api.d361api.base_information import BaseInformation
    __all__ = ['BaseInformation']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        BaseInformation = getattr(d361api, 'BaseInformation', None)
        if BaseInformation is None:
            raise ImportError(f"Could not find BaseInformation in d361api module")
        __all__ = ['BaseInformation']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import BaseInformation: {e}", ImportWarning)
        __all__ = []
