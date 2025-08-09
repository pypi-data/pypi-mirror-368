"""
Compatibility module for MediaFoldersDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.media_folders_data_customer.
"""

try:
    from d361api.d361api.media_folders_data_customer import MediaFoldersDataCustomer
    __all__ = ['MediaFoldersDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        MediaFoldersDataCustomer = getattr(d361api, 'MediaFoldersDataCustomer', None)
        if MediaFoldersDataCustomer is None:
            raise ImportError(f"Could not find MediaFoldersDataCustomer in d361api module")
        __all__ = ['MediaFoldersDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import MediaFoldersDataCustomer: {e}", ImportWarning)
        __all__ = []
