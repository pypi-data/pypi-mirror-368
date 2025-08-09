"""
Compatibility module for Hit.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.hit.
"""

try:
    from d361api.d361api.hit import Hit
    __all__ = ['Hit']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        Hit = getattr(d361api, 'Hit', None)
        if Hit is None:
            raise ImportError(f"Could not find Hit in d361api module")
        __all__ = ['Hit']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import Hit: {e}", ImportWarning)
        __all__ = []
