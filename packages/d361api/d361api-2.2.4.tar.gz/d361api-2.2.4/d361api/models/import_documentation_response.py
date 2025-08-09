"""
Compatibility module for ImportDocumentationResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.import_documentation_response.
"""

try:
    from d361api.d361api.import_documentation_response import ImportDocumentationResponse
    __all__ = ['ImportDocumentationResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ImportDocumentationResponse = getattr(d361api, 'ImportDocumentationResponse', None)
        if ImportDocumentationResponse is None:
            raise ImportError(f"Could not find ImportDocumentationResponse in d361api module")
        __all__ = ['ImportDocumentationResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ImportDocumentationResponse: {e}", ImportWarning)
        __all__ = []
