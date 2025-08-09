"""
Compatibility module for ExportDocumentationRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.export_documentation_request.
"""

try:
    from d361api.d361api.export_documentation_request import ExportDocumentationRequest
    __all__ = ['ExportDocumentationRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ExportDocumentationRequest = getattr(d361api, 'ExportDocumentationRequest', None)
        if ExportDocumentationRequest is None:
            raise ImportError(f"Could not find ExportDocumentationRequest in d361api module")
        __all__ = ['ExportDocumentationRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ExportDocumentationRequest: {e}", ImportWarning)
        __all__ = []
