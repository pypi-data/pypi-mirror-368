"""
Compatibility module for LanguageSummaryCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.language_summary_customer.
"""

try:
    from d361api.d361api.language_summary_customer import LanguageSummaryCustomer
    __all__ = ['LanguageSummaryCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        LanguageSummaryCustomer = getattr(d361api, 'LanguageSummaryCustomer', None)
        if LanguageSummaryCustomer is None:
            raise ImportError(f"Could not find LanguageSummaryCustomer in d361api module")
        __all__ = ['LanguageSummaryCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import LanguageSummaryCustomer: {e}", ImportWarning)
        __all__ = []
