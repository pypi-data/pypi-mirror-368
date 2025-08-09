"""
Compatibility module for AccessScopeLevel.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.access_scope_level.
"""

try:
    from d361api.d361api.access_scope_level import AccessScopeLevel
    __all__ = ['AccessScopeLevel']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AccessScopeLevel = getattr(d361api, 'AccessScopeLevel', None)
        if AccessScopeLevel is None:
            raise ImportError(f"Could not find AccessScopeLevel in d361api module")
        __all__ = ['AccessScopeLevel']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AccessScopeLevel: {e}", ImportWarning)
        __all__ = []
