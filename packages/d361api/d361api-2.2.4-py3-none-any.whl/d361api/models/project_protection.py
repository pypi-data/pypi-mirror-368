"""
Compatibility module for ProjectProtection.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.project_protection.
"""

try:
    from d361api.d361api.project_protection import ProjectProtection
    __all__ = ['ProjectProtection']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ProjectProtection = getattr(d361api, 'ProjectProtection', None)
        if ProjectProtection is None:
            raise ImportError(f"Could not find ProjectProtection in d361api module")
        __all__ = ['ProjectProtection']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ProjectProtection: {e}", ImportWarning)
        __all__ = []
