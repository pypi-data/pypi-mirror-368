"""
Compatibility module for ContentRoleInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.content_role_info.
"""

try:
    from d361api.d361api.content_role_info import ContentRoleInfo
    __all__ = ['ContentRoleInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ContentRoleInfo = getattr(d361api, 'ContentRoleInfo', None)
        if ContentRoleInfo is None:
            raise ImportError(f"Could not find ContentRoleInfo in d361api module")
        __all__ = ['ContentRoleInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ContentRoleInfo: {e}", ImportWarning)
        __all__ = []
