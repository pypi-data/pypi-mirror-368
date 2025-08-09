"""
Compatibility module for MediaFilesMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_files_meta_data_customer.
"""

try:
    from d361api.d361api.media_files_meta_data_customer import MediaFilesMetaDataCustomer
    __all__ = ['MediaFilesMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFilesMetaDataCustomer = getattr(d361api, 'MediaFilesMetaDataCustomer', None)
        if MediaFilesMetaDataCustomer is None:
            raise ImportError(f"Could not find MediaFilesMetaDataCustomer in d361api module")
        __all__ = ['MediaFilesMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFilesMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
