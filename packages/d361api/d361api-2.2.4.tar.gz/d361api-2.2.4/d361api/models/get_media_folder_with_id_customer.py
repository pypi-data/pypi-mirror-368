"""
Compatibility module for GetMediaFolderWithIdCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_media_folder_with_id_customer.
"""

try:
    from d361api.d361api.get_media_folder_with_id_customer import GetMediaFolderWithIdCustomer
    __all__ = ['GetMediaFolderWithIdCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetMediaFolderWithIdCustomer = getattr(d361api, 'GetMediaFolderWithIdCustomer', None)
        if GetMediaFolderWithIdCustomer is None:
            raise ImportError(f"Could not find GetMediaFolderWithIdCustomer in d361api module")
        __all__ = ['GetMediaFolderWithIdCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetMediaFolderWithIdCustomer: {e}", ImportWarning)
        __all__ = []
