"""
Compatibility module for SSOSchemeDetails.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.sso_scheme_details.
"""

try:
    from d361api.d361api.sso_scheme_details import SSOSchemeDetails
    __all__ = ['SSOSchemeDetails']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        SSOSchemeDetails = getattr(d361api, 'SSOSchemeDetails', None)
        if SSOSchemeDetails is None:
            raise ImportError(f"Could not find SSOSchemeDetails in d361api module")
        __all__ = ['SSOSchemeDetails']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import SSOSchemeDetails: {e}", ImportWarning)
        __all__ = []
