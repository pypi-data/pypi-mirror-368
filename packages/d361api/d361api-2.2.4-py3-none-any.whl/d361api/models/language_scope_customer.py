"""
Compatibility module for LanguageScopeCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language_scope_customer.
"""

try:
    from d361api.d361api.language_scope_customer import LanguageScopeCustomer
    __all__ = ['LanguageScopeCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        LanguageScopeCustomer = getattr(d361api, 'LanguageScopeCustomer', None)
        if LanguageScopeCustomer is None:
            raise ImportError(f"Could not find LanguageScopeCustomer in d361api module")
        __all__ = ['LanguageScopeCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import LanguageScopeCustomer: {e}", ImportWarning)
        __all__ = []
