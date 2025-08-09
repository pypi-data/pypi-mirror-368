"""
Compatibility module for MediaFileMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_file_meta_data_customer.
"""

try:
    from d361api.d361api.media_file_meta_data_customer import MediaFileMetaDataCustomer
    __all__ = ['MediaFileMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFileMetaDataCustomer = getattr(d361api, 'MediaFileMetaDataCustomer', None)
        if MediaFileMetaDataCustomer is None:
            raise ImportError(f"Could not find MediaFileMetaDataCustomer in d361api module")
        __all__ = ['MediaFileMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFileMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
