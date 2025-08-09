"""
Compatibility module for EmailExistsResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.email_exists_response.
"""

try:
    from d361api.d361api.email_exists_response import EmailExistsResponse
    __all__ = ['EmailExistsResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        EmailExistsResponse = getattr(d361api, 'EmailExistsResponse', None)
        if EmailExistsResponse is None:
            raise ImportError(f"Could not find EmailExistsResponse in d361api module")
        __all__ = ['EmailExistsResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import EmailExistsResponse: {e}", ImportWarning)
        __all__ = []
