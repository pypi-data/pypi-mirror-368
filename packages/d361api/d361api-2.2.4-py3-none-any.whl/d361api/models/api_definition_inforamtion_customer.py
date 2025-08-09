"""
Compatibility module for ApiDefinitionInforamtionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.api_definition_inforamtion_customer.
"""

try:
    from d361api.d361api.api_definition_inforamtion_customer import ApiDefinitionInforamtionCustomer
    __all__ = ['ApiDefinitionInforamtionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        ApiDefinitionInforamtionCustomer = getattr(d361api, 'ApiDefinitionInforamtionCustomer', None)
        if ApiDefinitionInforamtionCustomer is None:
            raise ImportError(f"Could not find ApiDefinitionInforamtionCustomer in d361api module")
        __all__ = ['ApiDefinitionInforamtionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import ApiDefinitionInforamtionCustomer: {e}", ImportWarning)
        __all__ = []
