"""
Compatibility module for ImportDocumentationLogAction.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.import_documentation_log_action.
"""

try:
    from d361api.d361api.import_documentation_log_action import ImportDocumentationLogAction
    __all__ = ['ImportDocumentationLogAction']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ImportDocumentationLogAction = getattr(d361api, 'ImportDocumentationLogAction', None)
        if ImportDocumentationLogAction is None:
            raise ImportError(f"Could not find ImportDocumentationLogAction in d361api module")
        __all__ = ['ImportDocumentationLogAction']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ImportDocumentationLogAction: {e}", ImportWarning)
        __all__ = []
