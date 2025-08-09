"""
Compatibility module for FeatureExplorerUserRoleEnum.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feature_explorer_user_role_enum.
"""

try:
    from d361api.d361api.feature_explorer_user_role_enum import FeatureExplorerUserRoleEnum
    __all__ = ['FeatureExplorerUserRoleEnum']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeatureExplorerUserRoleEnum = getattr(d361api, 'FeatureExplorerUserRoleEnum', None)
        if FeatureExplorerUserRoleEnum is None:
            raise ImportError(f"Could not find FeatureExplorerUserRoleEnum in d361api module")
        __all__ = ['FeatureExplorerUserRoleEnum']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeatureExplorerUserRoleEnum: {e}", ImportWarning)
        __all__ = []
