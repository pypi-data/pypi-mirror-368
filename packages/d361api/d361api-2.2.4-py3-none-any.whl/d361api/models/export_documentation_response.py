"""
Compatibility module for ExportDocumentationResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.export_documentation_response.
"""

try:
    from d361api.d361api.export_documentation_response import ExportDocumentationResponse
    __all__ = ['ExportDocumentationResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ExportDocumentationResponse = getattr(d361api, 'ExportDocumentationResponse', None)
        if ExportDocumentationResponse is None:
            raise ImportError(f"Could not find ExportDocumentationResponse in d361api module")
        __all__ = ['ExportDocumentationResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ExportDocumentationResponse: {e}", ImportWarning)
        __all__ = []
