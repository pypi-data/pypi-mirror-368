"""
Compatibility module for GetLogsDetailsResponseCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.get_logs_details_response_customer.
"""

try:
    from d361api.d361api.get_logs_details_response_customer import GetLogsDetailsResponseCustomer
    __all__ = ['GetLogsDetailsResponseCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        GetLogsDetailsResponseCustomer = getattr(d361api, 'GetLogsDetailsResponseCustomer', None)
        if GetLogsDetailsResponseCustomer is None:
            raise ImportError(f"Could not find GetLogsDetailsResponseCustomer in d361api module")
        __all__ = ['GetLogsDetailsResponseCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import GetLogsDetailsResponseCustomer: {e}", ImportWarning)
        __all__ = []
