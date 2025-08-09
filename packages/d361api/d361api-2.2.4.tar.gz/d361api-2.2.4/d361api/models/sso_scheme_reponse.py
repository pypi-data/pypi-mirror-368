"""
Compatibility module for SSOSchemeReponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.sso_scheme_reponse.
"""

try:
    from d361api.d361api.sso_scheme_reponse import SSOSchemeReponse
    __all__ = ['SSOSchemeReponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        SSOSchemeReponse = getattr(d361api, 'SSOSchemeReponse', None)
        if SSOSchemeReponse is None:
            raise ImportError(f"Could not find SSOSchemeReponse in d361api module")
        __all__ = ['SSOSchemeReponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import SSOSchemeReponse: {e}", ImportWarning)
        __all__ = []
