"""
Compatibility module for AddTeamAccountCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.add_team_account_customer.
"""

try:
    from d361api.d361api.add_team_account_customer import AddTeamAccountCustomer
    __all__ = ['AddTeamAccountCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        AddTeamAccountCustomer = getattr(d361api, 'AddTeamAccountCustomer', None)
        if AddTeamAccountCustomer is None:
            raise ImportError(f"Could not find AddTeamAccountCustomer in d361api module")
        __all__ = ['AddTeamAccountCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import AddTeamAccountCustomer: {e}", ImportWarning)
        __all__ = []
