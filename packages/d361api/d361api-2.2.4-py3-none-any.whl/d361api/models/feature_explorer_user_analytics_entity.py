"""
Compatibility module for FeatureExplorerUserAnalyticsEntity.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.feature_explorer_user_analytics_entity.
"""

try:
    from d361api.d361api.feature_explorer_user_analytics_entity import FeatureExplorerUserAnalyticsEntity
    __all__ = ['FeatureExplorerUserAnalyticsEntity']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        FeatureExplorerUserAnalyticsEntity = getattr(d361api, 'FeatureExplorerUserAnalyticsEntity', None)
        if FeatureExplorerUserAnalyticsEntity is None:
            raise ImportError(f"Could not find FeatureExplorerUserAnalyticsEntity in d361api module")
        __all__ = ['FeatureExplorerUserAnalyticsEntity']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import FeatureExplorerUserAnalyticsEntity: {e}", ImportWarning)
        __all__ = []
