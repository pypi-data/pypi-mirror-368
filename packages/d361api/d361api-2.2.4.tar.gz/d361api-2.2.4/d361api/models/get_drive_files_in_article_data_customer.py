"""
Compatibility module for GetDriveFilesInArticleDataCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_drive_files_in_article_data_customer.
"""

try:
    from d361api.d361api.get_drive_files_in_article_data_customer import GetDriveFilesInArticleDataCustomer
    __all__ = ['GetDriveFilesInArticleDataCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetDriveFilesInArticleDataCustomer = getattr(d361api, 'GetDriveFilesInArticleDataCustomer', None)
        if GetDriveFilesInArticleDataCustomer is None:
            raise ImportError(f"Could not find GetDriveFilesInArticleDataCustomer in d361api module")
        __all__ = ['GetDriveFilesInArticleDataCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetDriveFilesInArticleDataCustomer: {e}", ImportWarning)
        __all__ = []
