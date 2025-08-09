"""
Compatibility module for MediaFolderMetaDataResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_folder_meta_data_response_customer.
"""

try:
    from d361api.d361api.media_folder_meta_data_response_customer import MediaFolderMetaDataResponseCustomer
    __all__ = ['MediaFolderMetaDataResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFolderMetaDataResponseCustomer = getattr(d361api, 'MediaFolderMetaDataResponseCustomer', None)
        if MediaFolderMetaDataResponseCustomer is None:
            raise ImportError(f"Could not find MediaFolderMetaDataResponseCustomer in d361api module")
        __all__ = ['MediaFolderMetaDataResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFolderMetaDataResponseCustomer: {e}", ImportWarning)
        __all__ = []
