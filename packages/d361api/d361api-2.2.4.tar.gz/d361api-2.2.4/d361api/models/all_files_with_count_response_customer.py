"""
Compatibility module for AllFilesWithCountResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.all_files_with_count_response_customer.
"""

try:
    from d361api.d361api.all_files_with_count_response_customer import AllFilesWithCountResponseCustomer
    __all__ = ['AllFilesWithCountResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AllFilesWithCountResponseCustomer = getattr(d361api, 'AllFilesWithCountResponseCustomer', None)
        if AllFilesWithCountResponseCustomer is None:
            raise ImportError(f"Could not find AllFilesWithCountResponseCustomer in d361api module")
        __all__ = ['AllFilesWithCountResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AllFilesWithCountResponseCustomer: {e}", ImportWarning)
        __all__ = []
