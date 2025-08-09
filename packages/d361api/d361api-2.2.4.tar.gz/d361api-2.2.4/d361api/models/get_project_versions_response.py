"""
Compatibility module for GetProjectVersionsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_project_versions_response.
"""

try:
    from d361api.d361api.get_project_versions_response import GetProjectVersionsResponse
    __all__ = ['GetProjectVersionsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetProjectVersionsResponse = getattr(d361api, 'GetProjectVersionsResponse', None)
        if GetProjectVersionsResponse is None:
            raise ImportError(f"Could not find GetProjectVersionsResponse in d361api module")
        __all__ = ['GetProjectVersionsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetProjectVersionsResponse: {e}", ImportWarning)
        __all__ = []
