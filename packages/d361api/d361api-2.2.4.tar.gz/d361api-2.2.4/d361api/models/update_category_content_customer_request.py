"""
Compatibility module for UpdateCategoryContentCustomerRequest.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_category_content_customer_request.
"""

try:
    from d361api.d361api.update_category_content_customer_request import UpdateCategoryContentCustomerRequest
    __all__ = ['UpdateCategoryContentCustomerRequest']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateCategoryContentCustomerRequest = getattr(d361api, 'UpdateCategoryContentCustomerRequest', None)
        if UpdateCategoryContentCustomerRequest is None:
            raise ImportError(f"Could not find UpdateCategoryContentCustomerRequest in d361api module")
        __all__ = ['UpdateCategoryContentCustomerRequest']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateCategoryContentCustomerRequest: {e}", ImportWarning)
        __all__ = []
