"""
Compatibility module for MediaFolderViewMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_folder_view_meta_data_customer.
"""

try:
    from d361api.d361api.media_folder_view_meta_data_customer import MediaFolderViewMetaDataCustomer
    __all__ = ['MediaFolderViewMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFolderViewMetaDataCustomer = getattr(d361api, 'MediaFolderViewMetaDataCustomer', None)
        if MediaFolderViewMetaDataCustomer is None:
            raise ImportError(f"Could not find MediaFolderViewMetaDataCustomer in d361api module")
        __all__ = ['MediaFolderViewMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFolderViewMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
