"""
Compatibility module for DeletedandStarredMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.deletedand_starred_meta_data_customer.
"""

try:
    from d361api.d361api.deletedand_starred_meta_data_customer import DeletedandStarredMetaDataCustomer
    __all__ = ['DeletedandStarredMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        DeletedandStarredMetaDataCustomer = getattr(d361api, 'DeletedandStarredMetaDataCustomer', None)
        if DeletedandStarredMetaDataCustomer is None:
            raise ImportError(f"Could not find DeletedandStarredMetaDataCustomer in d361api module")
        __all__ = ['DeletedandStarredMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import DeletedandStarredMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
