"""
Compatibility module for SSOUserTypes.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.sso_user_types.
"""

try:
    from d361api.d361api.sso_user_types import SSOUserTypes
    __all__ = ['SSOUserTypes']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        SSOUserTypes = getattr(d361api, 'SSOUserTypes', None)
        if SSOUserTypes is None:
            raise ImportError(f"Could not find SSOUserTypes in d361api module")
        __all__ = ['SSOUserTypes']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import SSOUserTypes: {e}", ImportWarning)
        __all__ = []
