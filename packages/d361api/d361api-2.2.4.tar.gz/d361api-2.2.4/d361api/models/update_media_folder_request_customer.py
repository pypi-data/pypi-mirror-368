"""
Compatibility module for UpdateMediaFolderRequestCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.update_media_folder_request_customer.
"""

try:
    from d361api.d361api.update_media_folder_request_customer import UpdateMediaFolderRequestCustomer
    __all__ = ['UpdateMediaFolderRequestCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        UpdateMediaFolderRequestCustomer = getattr(d361api, 'UpdateMediaFolderRequestCustomer', None)
        if UpdateMediaFolderRequestCustomer is None:
            raise ImportError(f"Could not find UpdateMediaFolderRequestCustomer in d361api module")
        __all__ = ['UpdateMediaFolderRequestCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import UpdateMediaFolderRequestCustomer: {e}", ImportWarning)
        __all__ = []
