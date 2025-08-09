"""
Compatibility module for GuideAccessInfo.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.guide_access_info.
"""

try:
    from d361api.d361api.guide_access_info import GuideAccessInfo
    __all__ = ['GuideAccessInfo']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GuideAccessInfo = getattr(d361api, 'GuideAccessInfo', None)
        if GuideAccessInfo is None:
            raise ImportError(f"Could not find GuideAccessInfo in d361api module")
        __all__ = ['GuideAccessInfo']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GuideAccessInfo: {e}", ImportWarning)
        __all__ = []
