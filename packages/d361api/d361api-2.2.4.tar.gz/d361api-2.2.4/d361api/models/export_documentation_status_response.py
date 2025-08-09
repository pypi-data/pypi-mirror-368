"""
Compatibility module for ExportDocumentationStatusResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.export_documentation_status_response.
"""

try:
    from d361api.d361api.export_documentation_status_response import ExportDocumentationStatusResponse
    __all__ = ['ExportDocumentationStatusResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ExportDocumentationStatusResponse = getattr(d361api, 'ExportDocumentationStatusResponse', None)
        if ExportDocumentationStatusResponse is None:
            raise ImportError(f"Could not find ExportDocumentationStatusResponse in d361api module")
        __all__ = ['ExportDocumentationStatusResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ExportDocumentationStatusResponse: {e}", ImportWarning)
        __all__ = []
