"""
Compatibility module for FeatureListEnum.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feature_list_enum.
"""

try:
    from d361api.d361api.feature_list_enum import FeatureListEnum
    __all__ = ['FeatureListEnum']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeatureListEnum = getattr(d361api, 'FeatureListEnum', None)
        if FeatureListEnum is None:
            raise ImportError(f"Could not find FeatureListEnum in d361api module")
        __all__ = ['FeatureListEnum']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeatureListEnum: {e}", ImportWarning)
        __all__ = []
