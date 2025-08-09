"""
Compatibility module for DeleteApiDefinitionCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.delete_api_definition_customer.
"""

try:
    from d361api.d361api.delete_api_definition_customer import DeleteApiDefinitionCustomer
    __all__ = ['DeleteApiDefinitionCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DeleteApiDefinitionCustomer = getattr(d361api, 'DeleteApiDefinitionCustomer', None)
        if DeleteApiDefinitionCustomer is None:
            raise ImportError(f"Could not find DeleteApiDefinitionCustomer in d361api module")
        __all__ = ['DeleteApiDefinitionCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DeleteApiDefinitionCustomer: {e}", ImportWarning)
        __all__ = []
