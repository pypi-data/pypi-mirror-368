"""
Compatibility module for AddMediaFolderRequestCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_media_folder_request_customer.
"""

try:
    from d361api.d361api.add_media_folder_request_customer import AddMediaFolderRequestCustomer
    __all__ = ['AddMediaFolderRequestCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddMediaFolderRequestCustomer = getattr(d361api, 'AddMediaFolderRequestCustomer', None)
        if AddMediaFolderRequestCustomer is None:
            raise ImportError(f"Could not find AddMediaFolderRequestCustomer in d361api module")
        __all__ = ['AddMediaFolderRequestCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddMediaFolderRequestCustomer: {e}", ImportWarning)
        __all__ = []
