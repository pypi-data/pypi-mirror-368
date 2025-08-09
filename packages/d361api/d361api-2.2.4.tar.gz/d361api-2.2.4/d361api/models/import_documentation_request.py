"""
Compatibility module for ImportDocumentationRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.import_documentation_request.
"""

try:
    from d361api.d361api.import_documentation_request import ImportDocumentationRequest
    __all__ = ['ImportDocumentationRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ImportDocumentationRequest = getattr(d361api, 'ImportDocumentationRequest', None)
        if ImportDocumentationRequest is None:
            raise ImportError(f"Could not find ImportDocumentationRequest in d361api module")
        __all__ = ['ImportDocumentationRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ImportDocumentationRequest: {e}", ImportWarning)
        __all__ = []
