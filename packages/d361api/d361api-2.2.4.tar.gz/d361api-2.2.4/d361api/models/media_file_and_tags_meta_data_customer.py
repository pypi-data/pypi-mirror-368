"""
Compatibility module for MediaFileAndTagsMetaDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_file_and_tags_meta_data_customer.
"""

try:
    from d361api.d361api.media_file_and_tags_meta_data_customer import MediaFileAndTagsMetaDataCustomer
    __all__ = ['MediaFileAndTagsMetaDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFileAndTagsMetaDataCustomer = getattr(d361api, 'MediaFileAndTagsMetaDataCustomer', None)
        if MediaFileAndTagsMetaDataCustomer is None:
            raise ImportError(f"Could not find MediaFileAndTagsMetaDataCustomer in d361api module")
        __all__ = ['MediaFileAndTagsMetaDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFileAndTagsMetaDataCustomer: {e}", ImportWarning)
        __all__ = []
