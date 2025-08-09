"""
Compatibility module for AllFilesWithCountCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.all_files_with_count_customer.
"""

try:
    from d361api.d361api.all_files_with_count_customer import AllFilesWithCountCustomer
    __all__ = ['AllFilesWithCountCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AllFilesWithCountCustomer = getattr(d361api, 'AllFilesWithCountCustomer', None)
        if AllFilesWithCountCustomer is None:
            raise ImportError(f"Could not find AllFilesWithCountCustomer in d361api module")
        __all__ = ['AllFilesWithCountCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AllFilesWithCountCustomer: {e}", ImportWarning)
        __all__ = []
