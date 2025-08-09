"""
Compatibility module for EmailExists.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.email_exists.
"""

try:
    from d361api.d361api.email_exists import EmailExists
    __all__ = ['EmailExists']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EmailExists = getattr(d361api, 'EmailExists', None)
        if EmailExists is None:
            raise ImportError(f"Could not find EmailExists in d361api module")
        __all__ = ['EmailExists']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EmailExists: {e}", ImportWarning)
        __all__ = []
