"""
Compatibility module for TeamAccountGroupSummaryCustomer.

This module provides a compatibility import for the model that is actually located
in d361api.d361api.team_account_group_summary_customer.
"""

try:
    from d361api.d361api.team_account_group_summary_customer import TeamAccountGroupSummaryCustomer
    __all__ = ['TeamAccountGroupSummaryCustomer']
except ImportError:
    # If direct import fails, try to get it from main d361api module
    try:
        import d361api
        TeamAccountGroupSummaryCustomer = getattr(d361api, 'TeamAccountGroupSummaryCustomer', None)
        if TeamAccountGroupSummaryCustomer is None:
            raise ImportError(f"Could not find TeamAccountGroupSummaryCustomer in d361api module")
        __all__ = ['TeamAccountGroupSummaryCustomer']
    except (ImportError, AttributeError) as e:
        import warnings
        warnings.warn(f"Failed to import TeamAccountGroupSummaryCustomer: {e}", ImportWarning)
        __all__ = []
