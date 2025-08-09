"""
Compatibility module for UpdateCategoryContentCustomerResponse.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_category_content_customer_response.
"""

try:
    from d361api.d361api.update_category_content_customer_response import UpdateCategoryContentCustomerResponse
    __all__ = ['UpdateCategoryContentCustomerResponse']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateCategoryContentCustomerResponse = getattr(d361api, 'UpdateCategoryContentCustomerResponse', None)
        if UpdateCategoryContentCustomerResponse is None:
            raise ImportError(f"Could not find UpdateCategoryContentCustomerResponse in d361api module")
        __all__ = ['UpdateCategoryContentCustomerResponse']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateCategoryContentCustomerResponse: {e}", ImportWarning)
        __all__ = []
