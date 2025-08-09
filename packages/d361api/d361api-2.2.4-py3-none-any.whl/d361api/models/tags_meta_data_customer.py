"""
Compatibility module for TagsMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.tags_meta_data_customer.
"""

try:
    from d361api.d361api.tags_meta_data_customer import TagsMetaDataCustomer
    __all__ = ['TagsMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TagsMetaDataCustomer = getattr(d361api, 'TagsMetaDataCustomer', None)
        if TagsMetaDataCustomer is None:
            raise ImportError(f"Could not find TagsMetaDataCustomer in d361api module")
        __all__ = ['TagsMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TagsMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
