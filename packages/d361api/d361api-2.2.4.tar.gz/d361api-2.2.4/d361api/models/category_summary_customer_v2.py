"""
Compatibility module for CategorySummaryCustomerV2.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.category_summary_customer_v2.
"""

try:
    from d361api.d361api.category_summary_customer_v2 import CategorySummaryCustomerV2
    __all__ = ['CategorySummaryCustomerV2']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        CategorySummaryCustomerV2 = getattr(d361api, 'CategorySummaryCustomerV2', None)
        if CategorySummaryCustomerV2 is None:
            raise ImportError(f"Could not find CategorySummaryCustomerV2 in d361api module")
        __all__ = ['CategorySummaryCustomerV2']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import CategorySummaryCustomerV2: {e}", ImportWarning)
        __all__ = []
