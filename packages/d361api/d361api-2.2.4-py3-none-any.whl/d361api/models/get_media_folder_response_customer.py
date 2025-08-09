"""
Compatibility module for GetMediaFolderResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_media_folder_response_customer.
"""

try:
    from d361api.d361api.get_media_folder_response_customer import GetMediaFolderResponseCustomer
    __all__ = ['GetMediaFolderResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetMediaFolderResponseCustomer = getattr(d361api, 'GetMediaFolderResponseCustomer', None)
        if GetMediaFolderResponseCustomer is None:
            raise ImportError(f"Could not find GetMediaFolderResponseCustomer in d361api module")
        __all__ = ['GetMediaFolderResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetMediaFolderResponseCustomer: {e}", ImportWarning)
        __all__ = []
