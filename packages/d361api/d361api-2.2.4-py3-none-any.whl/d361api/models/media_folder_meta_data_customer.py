"""
Compatibility module for MediaFolderMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_folder_meta_data_customer.
"""

try:
    from d361api.d361api.media_folder_meta_data_customer import MediaFolderMetaDataCustomer
    __all__ = ['MediaFolderMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFolderMetaDataCustomer = getattr(d361api, 'MediaFolderMetaDataCustomer', None)
        if MediaFolderMetaDataCustomer is None:
            raise ImportError(f"Could not find MediaFolderMetaDataCustomer in d361api module")
        __all__ = ['MediaFolderMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFolderMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
