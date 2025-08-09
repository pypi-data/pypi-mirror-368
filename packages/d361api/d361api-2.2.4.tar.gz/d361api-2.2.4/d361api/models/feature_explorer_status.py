"""
Compatibility module for FeatureExplorerStatus.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feature_explorer_status.
"""

try:
    from d361api.d361api.feature_explorer_status import FeatureExplorerStatus
    __all__ = ['FeatureExplorerStatus']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeatureExplorerStatus = getattr(d361api, 'FeatureExplorerStatus', None)
        if FeatureExplorerStatus is None:
            raise ImportError(f"Could not find FeatureExplorerStatus in d361api module")
        __all__ = ['FeatureExplorerStatus']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeatureExplorerStatus: {e}", ImportWarning)
        __all__ = []
