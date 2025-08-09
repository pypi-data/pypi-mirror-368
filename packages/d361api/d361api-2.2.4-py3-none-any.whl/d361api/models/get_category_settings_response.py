"""
Compatibility module for GetCategorySettingsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_category_settings_response.
"""

try:
    from d361api.d361api.get_category_settings_response import GetCategorySettingsResponse
    __all__ = ['GetCategorySettingsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetCategorySettingsResponse = getattr(d361api, 'GetCategorySettingsResponse', None)
        if GetCategorySettingsResponse is None:
            raise ImportError(f"Could not find GetCategorySettingsResponse in d361api module")
        __all__ = ['GetCategorySettingsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetCategorySettingsResponse: {e}", ImportWarning)
        __all__ = []
