"""
Compatibility module for FeatureAnalytics.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feature_analytics.
"""

try:
    from d361api.d361api.feature_analytics import FeatureAnalytics
    __all__ = ['FeatureAnalytics']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeatureAnalytics = getattr(d361api, 'FeatureAnalytics', None)
        if FeatureAnalytics is None:
            raise ImportError(f"Could not find FeatureAnalytics in d361api module")
        __all__ = ['FeatureAnalytics']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeatureAnalytics: {e}", ImportWarning)
        __all__ = []
