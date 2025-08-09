"""
Compatibility module for MediaFileAndTagsMetaDataResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_file_and_tags_meta_data_response_customer.
"""

try:
    from d361api.d361api.media_file_and_tags_meta_data_response_customer import MediaFileAndTagsMetaDataResponseCustomer
    __all__ = ['MediaFileAndTagsMetaDataResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFileAndTagsMetaDataResponseCustomer = getattr(d361api, 'MediaFileAndTagsMetaDataResponseCustomer', None)
        if MediaFileAndTagsMetaDataResponseCustomer is None:
            raise ImportError(f"Could not find MediaFileAndTagsMetaDataResponseCustomer in d361api module")
        __all__ = ['MediaFileAndTagsMetaDataResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFileAndTagsMetaDataResponseCustomer: {e}", ImportWarning)
        __all__ = []
